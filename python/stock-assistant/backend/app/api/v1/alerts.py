"""告警历史路由：分页查询 + 详情 + WebSocket 实时推送。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.alert import Alert
from app.models.rule import AlertRule
from app.models.stock import Stock
from app.schemas.alert import AlertDetail, AlertListResponse, AlertOut
from app.ws.hub import alerts_hub

logger = logging.getLogger(__name__)

router = APIRouter()


def _alert_to_out(alert: Alert, rule_name: str | None = None) -> dict:
    """ORM 转 dict。"""
    snapshot = None
    if alert.snapshot:
        try:
            snapshot = json.loads(alert.snapshot)
        except (json.JSONDecodeError, TypeError):
            snapshot = None
    return {
        "id": alert.id,
        "code": alert.code,
        "ruleId": alert.rule_id,
        "ruleName": rule_name,
        "signalType": alert.signal_type,
        "triggerValue": alert.trigger_value,
        "threshold": alert.threshold,
        "price": alert.price,
        "snapshot": snapshot,
        "pushed": alert.pushed,
        "timestamp": alert.timestamp.isoformat() if hasattr(alert.timestamp, 'isoformat') else str(alert.timestamp),
    }


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    code: str | None = Query(default=None, description="按股票代码筛选"),
    signalType: str | None = Query(default=None, description="按信号类型筛选"),
    days: int = Query(default=7, ge=1, le=90, description="最近 N 天"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
) -> dict:
    """告警历史分页查询。"""
    since = datetime.now() - timedelta(days=days)

    # 构建 count 查询
    count_q = select(func.count(Alert.id)).where(Alert.timestamp >= since)
    if code:
        count_q = count_q.where(Alert.code == code)
    if signalType:
        count_q = count_q.where(Alert.signal_type == signalType)

    # 构建数据查询
    data_q = (
        select(Alert, AlertRule.name)
        .outerjoin(AlertRule, Alert.rule_id == AlertRule.id)
        .where(Alert.timestamp >= since)
    )
    if code:
        data_q = data_q.where(Alert.code == code)
    if signalType:
        data_q = data_q.where(Alert.signal_type == signalType)
    data_q = data_q.order_by(Alert.timestamp.desc()).limit(pageSize).offset((page - 1) * pageSize)

    async with AsyncSessionLocal() as session:
        total = (await session.execute(count_q)).scalar() or 0
        rows = (await session.execute(data_q)).all()

    items = [_alert_to_out(alert, rule_name) for alert, rule_name in rows]
    return {"total": total, "items": items}


@router.get("/today", response_model=list[AlertOut])
async def list_today_alerts() -> list[dict]:
    """获取今日告警（Dashboard 用）。"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    q = (
        select(Alert, AlertRule.name)
        .outerjoin(AlertRule, Alert.rule_id == AlertRule.id)
        .where(Alert.timestamp >= today_start)
        .order_by(Alert.timestamp.desc())
        .limit(50)
    )
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(q)).all()
    return [_alert_to_out(alert, rule_name) for alert, rule_name in rows]


@router.get("/{alert_id}", response_model=AlertDetail)
async def get_alert(alert_id: str) -> dict:
    """告警详情。"""
    q = (
        select(Alert, AlertRule.name, Stock.name)
        .outerjoin(AlertRule, Alert.rule_id == AlertRule.id)
        .outerjoin(Stock, Alert.code == Stock.code)
        .where(Alert.id == alert_id)
    )
    async with AsyncSessionLocal() as session:
        row = (await session.execute(q)).first()
    if not row:
        raise HTTPException(status_code=404, detail="告警不存在")

    alert, rule_name, stock_name = row
    result = _alert_to_out(alert, rule_name)
    result["name"] = stock_name
    return result


@router.websocket("/ws")
async def alerts_websocket(ws: WebSocket) -> None:
    """WebSocket 订阅实时告警推送。"""
    await alerts_hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:  # noqa: BLE001
        logger.debug("alerts ws 异常: %s", e)
    finally:
        alerts_hub.disconnect(ws)
