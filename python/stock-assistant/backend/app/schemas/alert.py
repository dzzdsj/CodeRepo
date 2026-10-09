"""告警记录 Pydantic 模型。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AlertOut(BaseModel):
    """告警记录响应。"""

    id: str
    code: str
    ruleId: str
    ruleName: str | None = None
    signalType: str
    triggerValue: float
    threshold: float
    price: float
    snapshot: dict[str, Any] | None = None
    pushed: bool
    timestamp: str  # ISO 格式

    model_config = {"from_attributes": True}


class AlertDetail(BaseModel):
    """告警详情（含行情快照）。"""

    id: str
    code: str
    name: str | None = None
    ruleId: str
    ruleName: str | None = None
    signalType: str
    triggerValue: float
    threshold: float
    price: float
    snapshot: dict[str, Any] | None = None
    pushed: bool
    timestamp: str


class AlertListResponse(BaseModel):
    """告警历史分页响应。"""

    total: int
    items: list[AlertOut]
