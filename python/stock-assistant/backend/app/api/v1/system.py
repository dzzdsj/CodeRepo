"""系统状态路由：调度状态 + 数据源连通性。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from app.services import data_source
from app.services.monitor import monitor
from app.ws.hub import alerts_hub, quotes_hub

router = APIRouter()


@router.get("/status")
async def system_status() -> dict:
    """返回调度器状态、缓存数量、是否交易时段。"""
    status = monitor.get_status()
    # 并行检查数据源连通性（不阻塞主流程过久）
    try:
        connectivity = await asyncio.wait_for(data_source.check_connectivity(), timeout=8)
    except asyncio.TimeoutError:
        connectivity = False
    status["dataSource"] = "akshare"
    status["dataSourceOk"] = connectivity
    status["wsClients"] = quotes_hub.count + alerts_hub.count
    return status
