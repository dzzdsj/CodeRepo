"""AI 分析服务：接入 LLM 对告警进行解读和操作建议。

支持的 Provider（均为 OpenAI 兼容接口）：
- zhipu（智谱 GLM）：https://open.bigmodel.cn/api/paas/v4/
- qwen（通义千问）：https://dashscope.aliyuncs.com/compatible-mode/v1/
- openai：https://api.openai.com/v1/
- deepseek：https://api.deepseek.com/v1/
- custom：用户自定义 base_url
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decrypt_token
from app.models.alert import Alert
from app.models.config import AiConfig
from app.services import data_source  # 复用 curl_post_async

logger = logging.getLogger(__name__)

# 各 Provider 默认配置
PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-flash",
        "label": "智谱 GLM",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/",
        "model": "qwen-turbo",
        "label": "通义千问",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/",
        "model": "gpt-4o-mini",
        "label": "OpenAI",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1/",
        "model": "deepseek-chat",
        "label": "DeepSeek",
    },
    "custom": {
        "base_url": "",
        "model": "",
        "label": "自定义",
    },
}


def _build_prompt(alert_data: dict) -> list[dict[str, str]]:
    """构建告警解读的 LLM Prompt。"""
    code = alert_data.get("code", "")
    name = alert_data.get("name", "")
    signal = alert_data.get("signalType", "")
    desc = alert_data.get("desc", "")
    price = alert_data.get("price", 0)
    trigger_value = alert_data.get("triggerValue", 0)
    threshold = alert_data.get("threshold", 0)
    snapshot = alert_data.get("snapshot", {})
    timestamp = alert_data.get("timestamp", "")

    signal_labels = {
        "change_pct": "涨跌幅阈值",
        "speed": "短时涨速异动",
        "volume": "成交量异常放大",
        "indicator": "技术指标突破",
    }

    system_prompt = (
        "你是一位专业的 A 股市场分析师。请根据告警信息，给出简洁、专业、客观的市场解读和操作建议。\n"
        "要求：\n"
        "1. 简要分析触发原因（涨停/跌停/资金流入流出/市场情绪等）\n"
        "2. 给出操作建议（加仓/减仓/观望/止损等，需说明理由）\n"
        "3. 提示风险（至少 1 条）\n"
        "4. 全文不超过 200 字，用中文回复\n"
        "5. 严格使用以下 JSON 格式输出，不要有任何额外文字：\n"
        '{"解读": "...", "建议": "...", "风险": "..."}'
    )

    user_prompt = (
        f"股票：{name}（{code}）\n"
        f"信号类型：{signal_labels.get(signal, signal)}\n"
        f"触发描述：{desc}\n"
        f"触发值：{trigger_value}\n"
        f"阈值：{threshold}\n"
        f"当前价格：{price}\n"
        f"行情快照：{json.dumps(snapshot, ensure_ascii=False)}\n"
        f"触发时间：{timestamp}\n"
        f"请给出你的专业解读。"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


class AiService:
    """AI 分析服务单例。"""

    async def _get_config(self) -> AiConfig | None:
        """获取 AI 配置。"""
        async with AsyncSessionLocal() as session:
            rows = await session.execute(select(AiConfig).limit(1))
            return rows.scalars().first()

    async def analyze_alert(self, alert_data: dict) -> dict | None:
        """对告警进行 AI 分析，返回解析后的 dict。

        Returns:
            {"解读": "...", "建议": "...", "风险": "..."} 或 None
        """
        config = await self._get_config()
        if not config or not config.enabled:
            logger.debug("AI 分析未启用，跳过")
            return None

        api_key = decrypt_token(config.api_key_encrypted)
        if not api_key:
            logger.warning("AI API Key 为空，跳过分析")
            return None

        base_url = config.base_url or PROVIDER_DEFAULTS.get(config.provider, {}).get(
            "base_url", ""
        )
        model = config.model or PROVIDER_DEFAULTS.get(config.provider, {}).get("model", "")

        if not base_url or not model:
            logger.error("AI base_url 或 model 为空")
            return None

        # 构建 OpenAI 兼容请求
        url = f"{base_url.rstrip('/')}/chat/completions"
        messages = _build_prompt(alert_data)
        payload = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 500,
                "response_format": {"type": "json_object"},
            },
            ensure_ascii=False,
        )

        try:
            resp = await data_source._curl_post_async(
                url,
                payload,
                timeout=30,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )
            if resp.status_code != 200:
                logger.error(
                    "AI API HTTP %d: %s",
                    resp.status_code,
                    resp.text[:300],
                )
                return None

            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if not content:
                logger.error("AI 返回内容为空")
                return None

            # 解析 JSON 响应
            try:
                result = json.loads(content)
                if not isinstance(result, dict):
                    result = {"解读": content}
                return result
            except json.JSONDecodeError:
                # 非 JSON 格式，直接作为解读文本
                return {"解读": content}

        except Exception as e:  # noqa: BLE001
            logger.error("AI 分析异常: %s", e)
            return None

    async def analyze_and_save(self, alert_id: str, alert_data: dict) -> dict | None:
        """分析告警并将结果存入数据库。"""
        result = await self.analyze_alert(alert_data)
        if result is None:
            return None

        async with AsyncSessionLocal() as session:
            rows = await session.execute(select(Alert).where(Alert.id == alert_id))
            alert = rows.scalars().first()
            if alert:
                alert.ai_analysis = json.dumps(result, ensure_ascii=False)
                alert.ai_analyzed_at = datetime.now()
                await session.commit()

        return result

    async def test_connection(self, provider: str, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """测试 AI 模型连通性。"""
        defaults = PROVIDER_DEFAULTS.get(provider, {})
        url = f"{(base_url or defaults.get('base_url', '')).rstrip('/')}/chat/completions"
        model_name = model or defaults.get("model", "")

        if not url or not model_name:
            return False, "base_url 或 model 为空"

        payload = json.dumps(
            {
                "model": model_name,
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 50,
            },
            ensure_ascii=False,
        )

        try:
            resp = await data_source._curl_post_async(
                url,
                payload,
                timeout=15,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )
            if resp.status_code == 200:
                return True, "AI 模型连通正常"
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:  # noqa: BLE001
            return False, f"连接失败: {e}"


# 全局单例
ai_service = AiService()
