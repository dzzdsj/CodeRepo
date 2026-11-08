from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    email: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    role_id: int | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=64)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    email: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    role_id: int | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None
    is_active: bool
    is_superuser: bool
    role: RoleBrief | None
    permissions: list[str]
    created_at: datetime
    updated_at: datetime


class UserListOut(BaseModel):
    total: int
    list: list[UserOut]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
