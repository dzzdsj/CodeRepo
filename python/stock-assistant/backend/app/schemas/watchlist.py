"""自选股 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class WatchlistCreate(BaseModel):
    code: str
    groupName: str = Field(default="默认", alias="groupName")
    note: str | None = None

    model_config = {"populate_by_name": True}


class WatchlistUpdate(BaseModel):
    groupName: str | None = None
    note: str | None = None

    model_config = {"populate_by_name": True}


class WatchlistItemOut(BaseModel):
    """自选股输出（含股票名，便于前端直接展示）。"""

    id: int
    code: str
    name: str
    groupName: str
    note: str | None = None
    sortOrder: int

    model_config = {"from_attributes": True, "populate_by_name": True}
