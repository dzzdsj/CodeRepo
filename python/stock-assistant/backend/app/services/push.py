"""推送服务：通过 Server酱/PushPlus 发送微信通知。

- Server酱：https://sct.ftqq.com/  — GET/POST https://sctapi.ftqq.com/{token}.send
- PushPlus：https://www.pushplus.plus/ — POST https://www.pushplus.plus/send
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decrypt_token, encrypt_token
from app.models.config import PushConfig
from app.services import data_source  # 复用 curl_get

logger = logging.getLogger(__name__)


class PushService:
    """微信推送服务单例。"""

    async def _get_config(self) -> PushConfig | None:
        """获取已启用的推送配置。"""
        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(PushConfig).where(PushConfig.enabled.is_(True)).limit(1)
            )
            return rows.scalars().first()

    async def send_alert(self, alert: dict) -> bool:
        """发送告警推送。返回是否成功。"""
        config = await self._get_config()
        if not config:
            logger.debug("推送配置未启用，跳过推送")
            return False

        token = decrypt_token(config.token_encrypted)
        if not token:
            logger.warning("推送 Token 为空，跳过推送")
            return False

        title, content = self._format_message(alert)

        try:
            if config.provider == "serverchan":
                return await self._send_serverchan(token, title, content)
            elif config.provider == "pushplus":
                return await self._send_pushplus(token, title, content)
            else:
                logger.error("未知推送渠道: %s", config.provider)
                return False
        except Exception as e:  # noqa: BLE001
            logger.error("推送发送失败: %s", e)
            return False

    async def send_test(self, token: str, provider: str) -> tuple[bool, str]:
        """发送测试推送。"""
        title = "股票助手测试推送"
        content = "如果您收到了这条消息，说明推送渠道配置正确！"

        try:
            if provider == "serverchan":
                ok = await self._send_serverchan(token, title, content)
            elif provider == "pushplus":
                ok = await self._send_pushplus(token, title, content)
            else:
                return False, f"未知推送渠道: {provider}"

            if ok:
                return True, "推送成功"
            return False, "推送失败，请检查 Token"
        except Exception as e:  # noqa: BLE001
            return False, f"推送异常: {e}"

    async def _send_serverchan(self, token: str, title: str, content: str) -> bool:
        """Server酱推送。"""
        url = f"https://sctapi.ftqq.com/{token}.send"
        try:
            resp = await data_source._curl_post_async(url, {"title": title, "desp": content})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("code", 0) == 0
            logger.warning("Server酱 HTTP %d: %s", resp.status_code, resp.text[:200])
            return False
        except Exception as e:  # noqa: BLE001
            logger.error("Server酱推送异常: %s", e)
            return False

    async def _send_pushplus(self, token: str, title: str, content: str) -> bool:
        """PushPlus 推送。"""
        import json

        url = "https://www.pushplus.plus/send"
        payload = json.dumps({
            "token": token,
            "title": title,
            "content": content,
            "template": "txt",
        })
        try:
            resp = await data_source._curl_post_async(
                url, payload, timeout=15, headers={"Content-Type": "application/json"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("code", 0) == 200
            logger.warning("PushPlus HTTP %d: %s", resp.status_code, resp.text[:200])
            return False
        except Exception as e:  # noqa: BLE001
            logger.error("PushPlus 推送异常: %s", e)
            return False

    def _format_message(self, alert: dict) -> tuple[str, str]:
        """格式化推送消息。"""
        code = alert.get("code", "")
        name = alert.get("name", "")
        desc = alert.get("desc", "")
        price = alert.get("price", 0)
        signal = alert.get("signalType", "")
        timestamp = alert.get("timestamp", "")

        title = f"【{name}】{desc}"
        content = (
            f"## {name}（{code}）\n\n"
            f"- 信号类型：{self._signal_label(signal)}\n"
            f"- 触发描述：{desc}\n"
            f"- 当前价格：{price:.2f}\n"
            f"- 触发时间：{timestamp}\n\n"
            f"请及时关注行情变化。"
        )
        return title, content

    def _signal_label(self, signal: str) -> str:
        labels = {
            "change_pct": "涨跌幅阈值",
            "speed": "短时涨速异动",
            "volume": "成交量异常放大",
            "indicator": "技术指标突破",
        }
        return labels.get(signal, signal)


# 全局单例
pusher = PushService()
