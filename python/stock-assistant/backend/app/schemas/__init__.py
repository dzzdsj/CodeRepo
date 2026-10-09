"""Pydantic 响应/请求模型聚合。"""

from app.schemas.alert import AlertDetail, AlertListResponse, AlertOut
from app.schemas.quote import IndexQuote, Quote
from app.schemas.rule import (
    AlertRuleCreate,
    AlertRuleOut,
    AlertRuleUpdate,
    RuleParams,
    RuleScope,
)
from app.schemas.settings import (
    PushConfigOut,
    PushConfigUpdate,
    PushTestResult,
    SchedulerConfigOut,
    SchedulerConfigUpdate,
)
from app.schemas.stock import StockOut, StockSearchResult
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemOut,
    WatchlistUpdate,
)

__all__ = [
    "Quote",
    "IndexQuote",
    "StockOut",
    "StockSearchResult",
    "WatchlistCreate",
    "WatchlistUpdate",
    "WatchlistItemOut",
    "AlertRuleCreate",
    "AlertRuleOut",
    "AlertRuleUpdate",
    "RuleParams",
    "RuleScope",
    "AlertOut",
    "AlertDetail",
    "AlertListResponse",
    "PushConfigOut",
    "PushConfigUpdate",
    "PushTestResult",
    "SchedulerConfigOut",
    "SchedulerConfigUpdate",
]
