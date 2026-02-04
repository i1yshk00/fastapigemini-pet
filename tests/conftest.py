import asyncio
import os
import tempfile
from pathlib import Path

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_session
from app.core.security import hash_password
from app.models import Users, GeminiRequests  # noqa: F401
from app.services.auth import create_access_token
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    tmp_dir = Path(tempfile.mkdtemp(prefix="fastapi_gemini_tests_"))
    db_path = tmp_dir / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())

    async def override_get_session():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.state.test_sessionmaker = SessionLocal

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    del app.state.test_sessionmaker
    asyncio.run(engine.dispose())
    try:
        db_path.unlink(missing_ok=True)
        tmp_dir.rmdir()
    except OSError:
        pass


@pytest.fixture
def sessionmaker(client):
    return app.state.test_sessionmaker


@pytest.fixture
def create_user(sessionmaker):
    def _create_user(
            email: str,
            password: str,
            is_admin: bool = False,
            is_active: bool = True,
    ):
        async def _inner():
            async with sessionmaker() as session:
                user = Users(
                    email=email,
                    hashed_password=hash_password(password),
                    is_admin=is_admin,
                    is_active=is_active,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
        return asyncio.run(_inner())
    return _create_user


@pytest.fixture
def create_gemini_request(sessionmaker):
    def _create_request(
            user_id: int,
            prompt: str = "Hello",
            response: str = "OK",
            model_version: str = "gemini-3-flash-preview",
    ):
        async def _inner():
            async with sessionmaker() as session:
                item = GeminiRequests(
                    user_id=user_id,
                    prompt=prompt,
                    response=response,
                    model_version=model_version,
                )
                session.add(item)
                await session.commit()
                await session.refresh(item)
                return item
        return asyncio.run(_inner())
    return _create_request


@pytest.fixture
def make_token():
    def _make_token(user: Users) -> str:
        token, _ = create_access_token(
            user_id=user.id,
            is_admin=user.is_admin,
        )
        return token
    return _make_token
