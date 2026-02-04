from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.auth import RegisterRequest, RegisterResponse, TokenResponse
from app.core.security import hash_password, MAX_PASSWORD_LENGTH
from app.repositories.user import get_user_by_email, create_user, update_last_login
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register', response_model=RegisterResponse)
async def register(
        data: RegisterRequest,
        session: AsyncSession = Depends(get_session)
):
    if await get_user_by_email(session, data.email):
        raise HTTPException(400, 'User already exists')

    if len(data.password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is too long",
        )

    user = await create_user(
        session,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    return {
        'id': user.id,
        'email': user.email,
        'created_at': user.created_at,
    }


@router.post('/login', response_model=TokenResponse)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(
        session,
        form_data.username,
        form_data.password,
    )
    if user is None:
        raise HTTPException(401, 'Invalid email or password')
    if not user.is_active:
        raise HTTPException(403, 'User is inactive')

    token, expires_in = create_access_token(
        user_id=user.id,
        is_admin=user.is_admin,
    )
    await update_last_login(session, user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }
