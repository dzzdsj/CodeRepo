from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocBase(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1)
    source: str | None = Field(default=None, max_length=256)
    doc_type: str = Field(default="text", max_length=32)
    is_enabled: bool = True


class KnowledgeDocCreate(KnowledgeDocBase):
    pass


class KnowledgeDocUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=256)
    content: str | None = Field(default=None, min_length=1)
    source: str | None = Field(default=None, max_length=256)
    doc_type: str | None = Field(default=None, max_length=32)
    is_enabled: bool | None = None


class KnowledgeDocOut(BaseModel):
    """列表场景不含 content 全文，减少传输量。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str | None
    doc_type: str
    status: str
    chunk_count: int
    is_enabled: bool
    remark: str | None
    created_at: datetime
    updated_at: datetime


class KnowledgeDocDetail(KnowledgeDocOut):
    """详情接口返回 content 全文。"""

    content: str


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class KnowledgeSearchResultItem(BaseModel):
    doc_id: int
    doc_title: str
    chunk_index: int
    chunk_content: str
    score: float


class KnowledgeAskRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class KnowledgeAskResponse(BaseModel):
    answer: str
    sources: list[KnowledgeSearchResultItem]
