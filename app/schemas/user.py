from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
    )


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=30,
        description="User password (min 8 chars, max 30)",
        examples=["StrongP@ssw0rd"],
    )


class UserRead(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class UserAdminRead(UserRead):
    pass


class UserAccessUpdate(BaseModel):
    is_active: bool | None = Field(
        None,
        description="Enable or disable user account",
        examples=[True],
    )
    is_admin: bool | None = Field(
        None,
        description="Grant or revoke admin privileges",
        examples=[False],
    )


class UserListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[UserAdminRead]
