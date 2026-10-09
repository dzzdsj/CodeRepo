"""AI 分析路由：告警 AI 解读 + AI 模型配置。"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decrypt_token, encrypt_token
from app.models.alert import Alert
from app.models.config import AiConfig
from app.models.rule import AlertRule
from app.models.stock import Stock
from app.services.ai import PROVIDER_DEFAULTS, ai_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ════════════════════════════════════════
#  AI 告警解读
# ════════════════════════════════════════


class AiAnalysisResponse(BaseModel):
    """AI 分析结果。"""

    alertId: str
    hasAnalysis: bool
    analysis: dict[str, str] | None = None
    analyzedAt: str | None = None


class AiAnalysisRequest(BaseModel):
    """请求 AI 分析（手动触发）。"""

    force: bool = Field(default=False, description="强制重新分析（忽略已有结果）")


@router.get("/alerts/{alert_id}/ai", response_model=AiAnalysisResponse)
async def get_ai_analysis(alert_id: str) -> dict:
    """获取告警的 AI 分析结果（如果已存在）。"""
    q = (
        select(Alert, AlertRule.name)
        .outerjoin(AlertRule, Alert.rule_id == AlertRule.id)
        .where(Alert.id == alert_id)
    )
    async with AsyncSessionLocal() as session:
        row = (await session.execute(q)).first()

    if not row:
        raise HTTPException(status_code=404, detail="告警不存在")

    alert, _ = row
    has_analysis = bool(alert.ai_analysis)
    analysis = None
    analyzed_at = None

    if has_analysis:
        try:
            analysis = json.loads(alert.ai_analysis)
        except (json.JSONDecodeError, TypeError):
            analysis = {"解读": alert.ai_analysis}
        if alert.ai_analyzed_at:
            analyzed_at = alert.ai_analyzed_at.isoformat()

    return {
        "alertId": alert_id,
        "hasAnalysis": has_analysis,
        "analysis": analysis,
        "analyzedAt": analyzed_at,
    }


@router.post("/alerts/{alert_id}/ai", response_model=AiAnalysisResponse)
async def trigger_ai_analysis(alert_id: str, body: AiAnalysisRequest) -> dict:
    """手动触发 AI 分析。"""
    # 查询告警 + 规则名 + 股票名
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

    # 已有分析且不强制刷新
    if alert.ai_analysis and not body.force:
        try:
            analysis = json.loads(alert.ai_analysis)
        except (json.JSONDecodeError, TypeError):
            analysis = {"解读": alert.ai_analysis}
        return {
            "alertId": alert_id,
            "hasAnalysis": True,
            "analysis": analysis,
            "analyzedAt": alert.ai_analyzed_at.isoformat() if alert.ai_analyzed_at else None,
        }

    # 构建告警数据
    snapshot = None
    if alert.snapshot:
        try:
            snapshot = json.loads(alert.snapshot)
        except (json.JSONDecodeError, TypeError):
            snapshot = None

    signal_labels = {
        "change_pct": "涨跌幅阈值",
        "speed": "短时涨速异动",
        "volume": "成交量异常放大",
        "indicator": "技术指标突破",
    }

    alert_data = {
        "code": alert.code,
        "name": stock_name or "",
        "ruleName": rule_name or "",
        "signalType": alert.signal_type,
        "desc": f"{signal_labels.get(alert.signal_type, alert.signal_type)} 触发值 {alert.trigger_value}",
        "triggerValue": alert.trigger_value,
        "threshold": alert.threshold,
        "price": alert.price,
        "snapshot": snapshot,
        "timestamp": alert.timestamp.isoformat(),
    }

    # 调用 AI 分析
    result = await ai_service.analyze_and_save(alert_id, alert_data)
    if result is None:
        raise HTTPException(
            status_code=503,
            detail="AI 分析失败：未配置 AI 模型或 API Key，或请求超时",
        )

    return {
        "alertId": alert_id,
        "hasAnalysis": True,
        "analysis": result,
        "analyzedAt": datetime.now().isoformat(),
    }


# ════════════════════════════════════════
#  AI 模型配置
# ════════════════════════════════════════


class AiConfigOut(BaseModel):
    """AI 配置响应。"""

    provider: str
    baseUrl: str
    model: str
    enabled: bool
    hasApiKey: bool


class AiConfigUpdate(BaseModel):
    """更新 AI 配置。"""

    provider: str = "zhipu"
    apiKey: str = ""
    baseUrl: str = ""
    model: str = ""
    enabled: bool = False


class AiTestResult(BaseModel):
    """AI 连通测试结果。"""

    success: bool
    message: str


@router.get("/settings/ai", response_model=AiConfigOut)
async def get_ai_config() -> dict:
    """获取 AI 模型配置。"""
    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AiConfig).limit(1))
        config = rows.scalars().first()

    if not config:
        defaults = PROVIDER_DEFAULTS["zhipu"]
        return {
            "provider": "zhipu",
            "baseUrl": defaults["base_url"],
            "model": defaults["model"],
            "enabled": False,
            "hasApiKey": False,
        }
    return {
        "provider": config.provider,
        "baseUrl": config.base_url,
        "model": config.model,
        "enabled": config.enabled,
        "hasApiKey": bool(config.api_key_encrypted),
    }


@router.put("/settings/ai", response_model=AiConfigOut)
async def update_ai_config(body: AiConfigUpdate) -> dict:
    """更新 AI 模型配置。"""
    defaults = PROVIDER_DEFAULTS.get(body.provider, {})
    base_url = body.baseUrl or defaults.get("base_url", "")
    model = body.model or defaults.get("model", "")

    async with AsyncSessionLocal() as session:
        rows = await session.execute(select(AiConfig).limit(1))
        config = rows.scalars().first()

        if not config:
            config = AiConfig(
                provider=body.provider,
                base_url=base_url,
                model=model,
                enabled=body.enabled,
            )
            session.add(config)
        else:
            config.provider = body.provider
            config.base_url = base_url
            config.model = model
            config.enabled = body.enabled

        if body.apiKey:
            config.api_key_encrypted = encrypt_token(body.apiKey)

        await session.commit()

    logger.info("AI 配置已更新: provider=%s, model=%s, enabled=%s", body.provider, model, body.enabled)
    return {
        "provider": config.provider,
        "baseUrl": config.base_url,
        "model": config.model,
        "enabled": config.enabled,
        "hasApiKey": bool(config.api_key_encrypted),
    }


@router.post("/settings/ai/test", response_model=AiTestResult)
async def test_ai_connection(
    provider: str = "zhipu",
    apiKey: str = "",
    baseUrl: str = "",
    model: str = "",
) -> dict:
    """测试 AI 模型连通性。"""
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    final_key = apiKey
    final_url = baseUrl or defaults.get("base_url", "")
    final_model = model or defaults.get("model", "")

    # 如果未提供 apiKey，使用已保存的
    if not final_key:
        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(AiConfig).where(AiConfig.provider == provider).limit(1)
            )
            config = rows.scalars().first()
        if config:
            final_key = decrypt_token(config.api_key_encrypted)

    if not final_key:
        return {"success": False, "message": "API Key 未配置"}

    success, message = await ai_service.test_connection(
        provider, final_key, final_url, final_model
    )
    return {"success": success, "message": message}


@router.get("/settings/ai/providers")
async def list_providers() -> list[dict]:
    """列出所有支持的 AI Provider。"""
    return [
        {"value": k, "label": v["label"], "baseUrl": v["base_url"], "model": v["model"]}
        for k, v in PROVIDER_DEFAULTS.items()
    ]
