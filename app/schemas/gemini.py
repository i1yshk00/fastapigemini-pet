from pydantic import BaseModel, Field
from datetime import datetime


class GeminiRequestBase(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Prompt sent to Gemini model",
        examples=["Explain async Python in simple words"],
    )

    model_version: str | None = Field(
        None,
        description="Gemini model version",
        max_length=128,
        examples=["gemini-3-flash-preview"],
    )


class GeminiRequestCreate(GeminiRequestBase):
    pass


class GeminiRequestRead(GeminiRequestBase):
    id: int
    request_id: str
    response: str = Field(
        ...,
        description="Model response text",
    )
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class GeminiHistoryItem(BaseModel):
    id: int
    request_id: str
    prompt: str
    response: str
    model_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GeminiHistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[GeminiHistoryItem]
