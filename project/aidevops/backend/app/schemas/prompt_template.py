from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=256)
    content: str = Field(min_length=1)
    is_enabled: bool = True


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=256)
    content: str | None = Field(default=None, min_length=1)
    is_enabled: bool | None = None


class PromptTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    content: str
    variables: list[str]
    version: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


class PromptTemplateRenderRequest(BaseModel):
    values: dict[str, str] = Field(default_factory=dict)


class PromptTemplateRenderResponse(BaseModel):
    rendered: str
