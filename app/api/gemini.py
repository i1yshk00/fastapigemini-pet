from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.gemini import (
    create_gemini_request,
    list_gemini_requests,
)
from app.schemas.gemini import (
    GeminiRequestCreate,
    GeminiRequestRead,
    GeminiHistoryResponse,
)
from app.services.auth import get_current_active_user
from app.services.gemini_client import request_gemini, GeminiServiceError

router = APIRouter(prefix="/gemini", tags=["Gemini"])


@router.post("/requests", response_model=GeminiRequestRead)
async def send_prompt(
        payload: GeminiRequestCreate,
        session: AsyncSession = Depends(get_session),
        current_user=Depends(get_current_active_user),
):
    model_version = payload.model_version or "gemini-3-flash-preview"
    try:
        answer = await request_gemini(
            prompt=payload.prompt,
            model_version=model_version,
        )
    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )

    item = await create_gemini_request(
        session=session,
        user_id=current_user.id,
        prompt=payload.prompt,
        response=answer,
        model_version=model_version,
    )
    return item


@router.get("/requests", response_model=GeminiHistoryResponse)
async def get_my_requests(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        session: AsyncSession = Depends(get_session),
        current_user=Depends(get_current_active_user),
):
    total, items = await list_gemini_requests(
        session=session,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }
