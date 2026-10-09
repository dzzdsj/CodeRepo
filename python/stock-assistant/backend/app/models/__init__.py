"""ORM 模型聚合导入，便于 Alembic 与应用统一导入。"""

from app.models.stock import Stock
from app.models.watchlist import WatchlistItem
from app.models.rule import AlertRule
from app.models.alert import Alert
from app.models.config import AiConfig, PushConfig, SchedulerConfig

__all__ = [
    "Stock",
    "WatchlistItem",
    "AlertRule",
    "Alert",
    "PushConfig",
    "SchedulerConfig",
    "AiConfig",
]
