"""行情相关路由：实时行情快照 + WebSocket 推送 + 技术指标 + K线 + 资金流向。"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.stock import Stock
from app.schemas.quote import FundFlowItem, FundFlowResponse, IndexQuote, Quote
from app.services import data_source
from app.services.indicators import get_indicator_signals
from app.services.monitor import monitor
from app.ws.hub import quotes_hub

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/realtime", response_model=list[Quote])
async def get_realtime_quotes() -> list[Quote]:
    """获取自选股最新行情快照（来自内存缓存）。"""
    return monitor.get_quotes()


@router.get("/indicators/{code}")
async def get_indicators(code: str) -> dict:
    """获取指定股票的技术指标数据。"""
    history = monitor.get_history(code)
    signals = get_indicator_signals(history)
    return {
        "code": code,
        "historyLen": len(history),
        "indicators": signals,
    }


@router.get("/kline/{code}")
async def get_kline(
    code: str,
    days: int = Query(default=60, ge=10, le=365),
) -> dict:
    """获取日 K 线数据（用于告警历史详情 K 线图）。"""
    kline = await data_source.fetch_daily_kline(code, days)
    return {
        "code": code,
        "days": days,
        "count": len(kline),
        "data": kline,
    }


@router.get("/fund-flow/{code}", response_model=FundFlowResponse)
async def get_fund_flow(
    code: str,
    days: int = Query(default=30, ge=5, le=120),
    session: AsyncSession = Depends(get_session),
) -> FundFlowResponse:
    """获取个股资金流向数据（主力/超大单/大单/中单/小单净流入）。

    - latest: 最新一日资金流向
    - history: 最近 days 天资金流向历史
    """
    # 获取股票名称
    stock = await session.get(Stock, code)
    name = stock.name if stock else code

    raw = await data_source.fetch_fund_flow(code, days)
    items = [FundFlowItem(**r) for r in raw]
    latest = items[-1] if items else None
    return FundFlowResponse(code=code, name=name, latest=latest, history=items)


@router.websocket("/ws")
async def quotes_websocket(ws: WebSocket) -> None:
    """WebSocket 订阅实时行情与指数推送。

    连接后立即收到一次当前缓存快照（quotes + indexes），随后按调度持续推送增量。
    """
    await quotes_hub.connect(ws)
    try:
        # 首次推送快照
        await ws.send_text(
            _encode({"type": "snapshot", "quotes": [q.model_dump() for q in monitor.get_quotes()],
                      "indexes": [i.model_dump() for i in monitor.get_indexes()]})
        )
        # 保持连接，被动接收广播；同时处理客户端心跳
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:  # noqa: BLE001
        logger.debug("quotes ws 异常: %s", e)
    finally:
        quotes_hub.disconnect(ws)


def _encode(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, default=str)
