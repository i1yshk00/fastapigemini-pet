from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gemini import GeminiRequests


async def create_gemini_request(
        session: AsyncSession,
        user_id: int,
        prompt: str,
        response: str,
        model_version: str,
) -> GeminiRequests:
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


async def get_gemini_request_by_id(
        session: AsyncSession,
        request_id: int,
        user_id: int | None = None,
) -> GeminiRequests | None:
    stmt = select(GeminiRequests).where(GeminiRequests.id == request_id)
    if user_id is not None:
        stmt = stmt.where(GeminiRequests.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_gemini_requests(
        session: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
) -> tuple[int, list[GeminiRequests]]:
    total_result = await session.execute(
        select(func.count())
        .select_from(GeminiRequests)
        .where(GeminiRequests.user_id == user_id)
    )
    total = total_result.scalar_one()

    items_result = await session.execute(
        select(GeminiRequests)
        .where(GeminiRequests.user_id == user_id)
        .order_by(GeminiRequests.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(items_result.scalars().all())
    return total, items


async def list_all_gemini_requests(
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        user_id: int | None = None,
) -> tuple[int, list[GeminiRequests]]:
    total_stmt = select(func.count()).select_from(GeminiRequests)
    if user_id is not None:
        total_stmt = total_stmt.where(GeminiRequests.user_id == user_id)
    total_result = await session.execute(total_stmt)
    total = total_result.scalar_one()

    items_stmt = select(GeminiRequests).order_by(
        GeminiRequests.created_at.desc()
    )
    if user_id is not None:
        items_stmt = items_stmt.where(GeminiRequests.user_id == user_id)
    items_result = await session.execute(
        items_stmt.offset(offset).limit(limit)
    )
    items = list(items_result.scalars().all())
    return total, items
