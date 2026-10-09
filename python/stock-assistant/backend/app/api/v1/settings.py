"""系统设置路由：推送配置 + 调度配置。"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decrypt_token, encrypt_token
from app.models.config import PushConfig, SchedulerConfig
from app.schemas.settings import (
    PushConfigOut,
    PushConfigUpdate,
    PushTestResult,
    SchedulerConfigOut,
    SchedulerConfigUpdate,
)
from app.services.push import pusher

logger = logging.getLogger(__name__)

router = APIRouter()


# ════════════════════════════════════════
#  推送配置
# ════════════════════════════════════════


@router.get("/push", response_model=PushConfigOut)
async def get_push_config() -> dict:
    """获取推送配置。"""
    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(PushConfig).limit(1))
        config = rows.scalars().first()

    if not config:
        return {"provider": "serverchan", "enabled": False, "hasToken": False}
    return {
        "provider": config.provider,
        "enabled": config.enabled,
        "hasToken": bool(config.token_encrypted),
    }


@router.put("/push", response_model=PushConfigOut)
async def update_push_config(body: PushConfigUpdate) -> dict:
    """更新推送配置。"""
    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(PushConfig).limit(1))
        config = rows.scalars().first()

        if not config:
            config = PushConfig(provider=body.provider, enabled=body.enabled)
            session.add(config)
        else:
            config.provider = body.provider
            config.enabled = body.enabled

        if body.token:
            config.token_encrypted = encrypt_token(body.token)

        await session.commit()

    logger.info("推送配置已更新: provider=%s, enabled=%s", body.provider, body.enabled)
    return {
        "provider": config.provider,
        "enabled": config.enabled,
        "hasToken": bool(config.token_encrypted),
    }


@router.post("/push/test", response_model=PushTestResult)
async def test_push(token: str = "", provider: str = "serverchan") -> dict:
    """发送测试推送。

    - 若提供 token 参数，用该 token 测试
    - 否则使用已保存的配置测试
    """
    if token:
        success, message = await pusher.send_test(token, provider)
        return {"success": success, "message": message}

    # 用已保存配置
    async with AsyncSessionLocal() as session:
        rows = await session.execute(
            select(PushConfig).where(PushConfig.enabled.is_(True)).limit(1)
        )
        config = rows.scalars().first()

    if not config:
        return {"success": False, "message": "未配置推送渠道或未启用"}
    saved_token = decrypt_token(config.token_encrypted)
    if not saved_token:
        return {"success": False, "message": "Token 未配置"}

    success, message = await pusher.send_test(saved_token, config.provider)
    return {"success": success, "message": message}


# ════════════════════════════════════════
#  调度配置
# ════════════════════════════════════════


@router.get("/scheduler", response_model=SchedulerConfigOut)
async def get_scheduler_config() -> dict:
    """获取调度配置。"""
    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(SchedulerConfig).where(SchedulerConfig.id == 1))
        config = rows.scalars().first()

    if not config:
        return {
            "dataSource": "akshare",
            "intervalSeconds": 5,
            "sessionStart": "09:30",
            "sessionEnd": "15:00",
        }
    return {
        "dataSource": config.data_source,
        "intervalSeconds": config.interval_seconds,
        "sessionStart": config.session_start,
        "sessionEnd": config.session_end,
    }


@router.put("/scheduler", response_model=SchedulerConfigOut)
async def update_scheduler_config(body: SchedulerConfigUpdate) -> dict:
    """更新调度配置。"""
    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(SchedulerConfig).where(SchedulerConfig.id == 1))
        config = rows.scalars().first()

        if not config:
            config = SchedulerConfig(id=1)
            session.add(config)

        if body.dataSource is not None:
            config.data_source = body.dataSource
        if body.intervalSeconds is not None:
            config.interval_seconds = body.intervalSeconds
        if body.sessionStart is not None:
            config.session_start = body.sessionStart
        if body.sessionEnd is not None:
            config.session_end = body.sessionEnd

        await session.commit()

    logger.info(
        "调度配置已更新: source=%s, interval=%ss",
        config.data_source,
        config.interval_seconds,
    )
    return {
        "dataSource": config.data_source,
        "intervalSeconds": config.interval_seconds,
        "sessionStart": config.session_start,
        "sessionEnd": config.session_end,
    }
