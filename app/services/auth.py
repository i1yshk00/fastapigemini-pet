from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.db.session import get_session
from app.repositories.user import get_user_by_email, get_user_by_id

bearer_scheme = HTTPBearer()


def create_access_token(
        user_id: int,
        is_admin: bool,
        expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, int(expires_delta.total_seconds())


async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
):
    user = await get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
        session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if not str(user_id).isdigit():
        raise credentials_exception

    user = await get_user_by_id(session, int(user_id))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user=Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return current_user


async def require_admin(
        current_user=Depends(get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
