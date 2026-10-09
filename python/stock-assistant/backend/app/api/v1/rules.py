"""告警规则路由：CRUD + 启用/禁用。"""

from __future__ import annotations

import json
import logging
import uuid

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.alert import Alert
from app.models.rule import AlertRule
from app.schemas.rule import (
    AlertRuleCreate,
    AlertRuleOut,
    AlertRuleUpdate,
)
from app.services.detector import detector
from app.services.push import pusher

logger = logging.getLogger(__name__)

router = APIRouter()


def _rule_to_out(rule: AlertRule) -> dict:
    """ORM 转 dict（字段名 camelCase）。"""
    params = json.loads(rule.params) if isinstance(rule.params, str) else rule.params
    scope = json.loads(rule.scope) if isinstance(rule.scope, str) else rule.scope
    channels = json.loads(rule.channels) if isinstance(rule.channels, str) else rule.channels
    return {
        "id": rule.id,
        "name": rule.name,
        "enabled": rule.enabled,
        "signalType": rule.signal_type,
        "params": params,
        "scope": scope,
        "sessionStart": rule.session_start,
        "sessionEnd": rule.session_end,
        "channels": channels,
        "cooldownMinutes": rule.cooldown_minutes,
    }


@router.get("", response_model=list[AlertRuleOut])
async def list_rules() -> list[dict]:
    """获取所有告警规则。"""
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AlertRule).order_by(AlertRule.updated_at.desc()))
        rules = rows.scalars().all()
    return [_rule_to_out(r) for r in rules]


@router.post("", response_model=AlertRuleOut, status_code=201)
async def create_rule(body: AlertRuleCreate) -> dict:
    """创建告警规则。"""
    rule_id = str(uuid.uuid4())
    params_json = json.dumps(body.params.model_dump(), ensure_ascii=False)
    scope_json = json.dumps(body.scope.model_dump(), ensure_ascii=False)
    channels_json = json.dumps(body.channels, ensure_ascii=False)

    rule = AlertRule(
        id=rule_id,
        name=body.name,
        enabled=body.enabled,
        signal_type=body.signalType,
        params=params_json,
        scope=scope_json,
        session_start=body.sessionStart,
        session_end=body.sessionEnd,
        channels=channels_json,
        cooldown_minutes=body.cooldownMinutes,
    )
    async with AsyncSessionLocal() as session:
        session.add(rule)
        await session.commit()
        await session.refresh(rule)
    await detector.refresh_rules()
    logger.info("创建规则: %s (%s)", body.name, rule_id)
    return _rule_to_out(rule)


@router.put("/{rule_id}", response_model=AlertRuleOut)
async def update_rule(rule_id: str, body: AlertRuleUpdate) -> dict:
    """更新告警规则。"""
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        rule = rows.scalars().first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")

        if body.name is not None:
            rule.name = body.name
        if body.enabled is not None:
            rule.enabled = body.enabled
        if body.signalType is not None:
            rule.signal_type = body.signalType
        if body.params is not None:
            rule.params = json.dumps(body.params.model_dump(), ensure_ascii=False)
        if body.scope is not None:
            rule.scope = json.dumps(body.scope.model_dump(), ensure_ascii=False)
        if body.sessionStart is not None:
            rule.session_start = body.sessionStart
        if body.sessionEnd is not None:
            rule.session_end = body.sessionEnd
        if body.channels is not None:
            rule.channels = json.dumps(body.channels, ensure_ascii=False)
        if body.cooldownMinutes is not None:
            rule.cooldown_minutes = body.cooldownMinutes

        await session.commit()
        await session.refresh(rule)

    await detector.refresh_rules()
    logger.info("更新规则: %s", rule_id)
    return _rule_to_out(rule)


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(rule_id: str) -> None:
    """删除告警规则。"""
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        rule = rows.scalars().first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        await session.delete(rule)
        await session.commit()

    await detector.refresh_rules()
    logger.info("删除规则: %s", rule_id)


@router.post("/{rule_id}/copy", response_model=AlertRuleOut, status_code=201)
async def copy_rule(rule_id: str) -> dict:
    """复制告警规则：保留所有参数，名称加后缀『副本』，默认禁用。"""
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        src = rows.scalars().first()
        if not src:
            raise HTTPException(status_code=404, detail="规则不存在")

        new_id = str(uuid.uuid4())
        new_rule = AlertRule(
            id=new_id,
            name=f"{src.name} 副本",
            enabled=False,  # 复制出的规则默认禁用
            signal_type=src.signal_type,
            params=src.params,
            scope=src.scope,
            session_start=src.session_start,
            session_end=src.session_end,
            channels=src.channels,
            cooldown_minutes=src.cooldown_minutes,
        )
        session.add(new_rule)
        await session.commit()
        await session.refresh(new_rule)

    await detector.refresh_rules()
    logger.info("复制规则: %s -> %s", rule_id, new_id)
    return _rule_to_out(new_rule)


@router.patch("/{rule_id}/toggle", response_model=AlertRuleOut)
async def toggle_rule(rule_id: str) -> dict:
    """启用/禁用规则。"""
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        rule = rows.scalars().first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        rule.enabled = not rule.enabled
        await session.commit()
        await session.refresh(rule)

    await detector.refresh_rules()
    return _rule_to_out(rule)


@router.get("/{rule_id}/stats")
async def get_rule_stats(rule_id: str) -> dict:
    """获取规则触发统计：总次数、今日、近7天、推送成功数、涉及股票数。"""
    async with AsyncSessionLocal() as session:
        # 校验规则存在
        rule = (
            await session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        ).scalars().first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")

        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today_start - timedelta(days=7)

        # 总触发数
        total = (
            await session.execute(
                select(func.count()).select_from(Alert).where(Alert.rule_id == rule_id)
            )
        ).scalar() or 0

        # 今日触发数
        today_count = (
            await session.execute(
                select(func.count())
                .select_from(Alert)
                .where(Alert.rule_id == rule_id, Alert.timestamp >= today_start)
            )
        ).scalar() or 0

        # 近 7 天触发数
        week_count = (
            await session.execute(
                select(func.count())
                .select_from(Alert)
                .where(Alert.rule_id == rule_id, Alert.timestamp >= week_ago)
            )
        ).scalar() or 0

        # 推送成功数
        pushed_count = (
            await session.execute(
                select(func.count())
                .select_from(Alert)
                .where(Alert.rule_id == rule_id, Alert.pushed.is_(True))
            )
        ).scalar() or 0

        # 涉及股票数
        stock_count = (
            await session.execute(
                select(func.count(func.distinct(Alert.code)))
                .select_from(Alert)
                .where(Alert.rule_id == rule_id)
            )
        ).scalar() or 0

    return {
        "ruleId": rule_id,
        "totalTriggers": total,
        "todayTriggers": today_count,
        "weekTriggers": week_count,
        "pushedCount": pushed_count,
        "pushRate": round(pushed_count / total * 100, 1) if total > 0 else 0,
        "stockCount": stock_count,
    }
