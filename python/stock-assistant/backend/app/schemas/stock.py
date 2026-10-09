"""股票基础库 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel


class StockOut(BaseModel):
    code: str
    name: str
    market: str
    industry: str | None = None

    model_config = {"from_attributes": True}


class StockSearchResult(BaseModel):
    code: str
    name: str
    market: str
    industry: str | None = None

    model_config = {"from_attributes": True}
