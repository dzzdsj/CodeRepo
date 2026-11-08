from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CodeReviewIssue(BaseModel):
    severity: str  # high / medium / low
    category: str  # bug / security / style / performance / other
    line: int | None = None
    description: str
    suggestion: str | None = None


class CodeReviewSuggestions(BaseModel):
    summary: str
    score: int | None = Field(default=None, ge=0, le=100)
    issues: list[CodeReviewIssue] = []


class CodeReviewCreate(BaseModel):
    repo: str = Field(min_length=1, max_length=256)
    code_content: str = Field(min_length=1)
    branch: str | None = Field(default=None, max_length=128)
    commit: str | None = Field(default=None, max_length=128)
    title: str | None = Field(default=None, max_length=256)
    language: str = Field(default="text", max_length=32)


class CodeReviewOut(BaseModel):
    """列表场景不含代码全文，减少传输量。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    repo: str
    branch: str | None
    commit: str | None
    title: str | None
    language: str
    status: str
    score: int | None
    ai_suggestions: dict | None
    created_at: datetime
    updated_at: datetime


class CodeReviewDetail(CodeReviewOut):
    """详情接口返回代码全文。"""

    code_content: str
