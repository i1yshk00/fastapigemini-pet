from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, func, select
from app.models.user import Users


async def get_user_by_email(
        session: AsyncSession,
        email: str,
) -> Users | None:
    result = await session.execute(
        select(Users).where(Users.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
        session: AsyncSession,
        user_id: int,
) -> Users | None:
    result = await session.execute(
        select(Users).where(Users.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
        session: AsyncSession,
        email: str,
        hashed_password: str,
) -> Users:
    user = Users(email=email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_last_login(
        session: AsyncSession,
        user_id: int,
) -> None:
    await session.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(last_login_at=func.now())
    )
    await session.commit()


async def set_user_active(
        session: AsyncSession,
        user_id: int,
        is_active: bool,
) -> None:
    await session.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(is_active=is_active)
    )
    await session.commit()


async def set_user_admin(
        session: AsyncSession,
        user_id: int,
        is_admin: bool,
) -> None:
    await session.execute(
        update(Users)
        .where(Users.id == user_id)
        .values(is_admin=is_admin)
    )
    await session.commit()


async def list_users(
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
) -> tuple[int, list[Users]]:
    total_result = await session.execute(
        select(func.count()).select_from(Users)
    )
    total = total_result.scalar_one()

    items_result = await session.execute(
        select(Users)
        .order_by(Users.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(items_result.scalars().all())
    return total, items
