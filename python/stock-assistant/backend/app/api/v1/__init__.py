"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import (
    ai,
    alerts,
    indexes,
    quotes,
    rules,
    sectors,
    settings,
    stocks,
    system,
    watchlist,
)

router = APIRouter()
router.include_router(quotes.router, prefix="/quotes", tags=["行情"])
router.include_router(indexes.router, prefix="/indexes", tags=["指数"])
router.include_router(watchlist.router, prefix="/watchlist", tags=["自选股"])
router.include_router(stocks.router, prefix="/stocks", tags=["股票"])
router.include_router(system.router, prefix="/system", tags=["系统"])
router.include_router(rules.router, prefix="/rules", tags=["告警规则"])
router.include_router(alerts.router, prefix="/alerts", tags=["告警历史"])
router.include_router(settings.router, prefix="/settings", tags=["系统设置"])
router.include_router(sectors.router, prefix="/sectors", tags=["板块资金"])
router.include_router(ai.router, tags=["AI 分析"])
