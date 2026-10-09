"""大盘指数路由。"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.quote import IndexQuote
from app.services.monitor import monitor

router = APIRouter()


@router.get("/realtime", response_model=list[IndexQuote])
async def get_realtime_indexes() -> list[IndexQuote]:
    """获取大盘指数实时行情（来自内存缓存）。"""
    return monitor.get_indexes()
