"""告警规则 Pydantic 模型。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RuleScope(BaseModel):
    """规则适用范围。"""

    codes: list[str] | None = Field(
        default=None, description="股票代码列表，None 或空列表表示全部自选股"
    )


class RuleParams(BaseModel):
    """规则参数（按信号类型不同取值）。"""

    threshold: float = Field(description="阈值：涨跌幅%/涨速%/量比倍数/指标阈值")
    windowMinutes: int | None = Field(default=5, description="涨速窗口（分钟）")
    volMultiple: float | None = Field(default=2.0, description="量比倍数")
    indicator: str | None = Field(default=None, description="指标类型 MA/MACD/RSI/KDJ")
    indicatorParams: dict[str, Any] | None = Field(default=None, description="指标参数")


class AlertRuleCreate(BaseModel):
    """创建告警规则。"""

    name: str = Field(max_length=128)
    enabled: bool = True
    signalType: str = Field(description="change_pct | speed | volume | indicator")
    params: RuleParams
    scope: RuleScope = Field(default_factory=RuleScope)
    sessionStart: str = "09:30"
    sessionEnd: str = "15:00"
    channels: list[str] = Field(default_factory=lambda: ["wechat", "web"])
    cooldownMinutes: int = 30


class AlertRuleUpdate(BaseModel):
    """更新告警规则（全量更新）。"""

    name: str | None = None
    enabled: bool | None = None
    signalType: str | None = None
    params: RuleParams | None = None
    scope: RuleScope | None = None
    sessionStart: str | None = None
    sessionEnd: str | None = None
    channels: list[str] | None = None
    cooldownMinutes: int | None = None


class AlertRuleOut(BaseModel):
    """告警规则响应。"""

    id: str
    name: str
    enabled: bool
    signalType: str
    params: dict[str, Any]
    scope: dict[str, Any]
    sessionStart: str
    sessionEnd: str
    channels: list[str]
    cooldownMinutes: int

    model_config = {"from_attributes": True}
