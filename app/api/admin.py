from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.gemini import list_all_gemini_requests
from app.repositories.user import (
    get_user_by_id,
    list_users,
    set_user_active,
    set_user_admin,
)
from app.schemas.gemini import GeminiHistoryResponse
from app.schemas.user import UserAdminRead, UserAccessUpdate, UserListResponse
from app.services.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=UserListResponse)
async def admin_list_users(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        session: AsyncSession = Depends(get_session),
        current_admin=Depends(require_admin),
):
    total, items = await list_users(
        session=session,
        limit=limit,
        offset=offset,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.get("/users/{user_id}", response_model=UserAdminRead)
async def admin_get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        current_admin=Depends(require_admin),
):
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/users/{user_id}/access", response_model=UserAdminRead)
async def admin_update_user_access(
        user_id: int,
        payload: UserAccessUpdate,
        session: AsyncSession = Depends(get_session),
        current_admin=Depends(require_admin),
):
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(404, "User not found")

    if current_admin.id == user_id:
        if payload.is_active is not None or payload.is_admin is not None:
            raise HTTPException(
                400,
                "You cannot change your own access flags",
            )

    if payload.is_active is not None:
        await set_user_active(session, user_id, payload.is_active)
    if payload.is_admin is not None:
        await set_user_admin(session, user_id, payload.is_admin)

    user = await get_user_by_id(session, user_id)
    return user


@router.get("/gemini/requests", response_model=GeminiHistoryResponse)
async def admin_list_gemini_requests(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        user_id: int | None = Query(None, ge=1),
        session: AsyncSession = Depends(get_session),
        current_admin=Depends(require_admin),
):
    total, items = await list_all_gemini_requests(
        session=session,
        limit=limit,
        offset=offset,
        user_id=user_id,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }
