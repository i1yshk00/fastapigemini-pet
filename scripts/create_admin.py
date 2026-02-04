import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import inspect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import update

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.models.user import Users
from app.repositories.user import get_user_by_email


async def ensure_admin(email: str, password: str) -> None:
    async with engine.connect() as conn:
        has_users = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("users")
        )
    if not has_users:
        raise RuntimeError(
            "Database schema is not initialized. "
            "Run `alembic upgrade head` first."
        )

    if not (8 <= len(password) <= 30):
        raise ValueError("Password length must be between 8 and 30 chars")

    async with AsyncSessionLocal() as session:
        user = await get_user_by_email(session, email)
        if user is None:
            try:
                hashed = hash_password(password)
            except ValueError as exc:
                raise ValueError(str(exc)) from exc

            user = Users(
                email=email,
                hashed_password=hashed,
                is_active=True,
                is_admin=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Created admin user: {user.email} (id={user.id})")
            return

        try:
            hashed = hash_password(password)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        await session.execute(
            update(Users)
            .where(Users.id == user.id)
            .values(
                is_admin=True,
                is_active=True,
                hashed_password=hashed,
            )
        )
        await session.commit()
        print(f"Updated user to admin: {user.email} (id={user.id})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or promote an admin user."
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    try:
        asyncio.run(ensure_admin(args.email, args.password))
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
