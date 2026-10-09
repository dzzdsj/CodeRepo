"""WebSocket 连接管理 Hub：管理行情/告警两类订阅连接，提供广播方法。"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """通用 WebSocket 连接管理器。"""

    def __init__(self) -> None:
        # 连接集合；value 可存放附加元数据
        self._connections: dict[WebSocket, dict[str, Any]] = {}

    async def connect(self, ws: WebSocket) -> None:
        """接受连接并加入集合。"""
        await ws.accept()
        self._connections[ws] = {}

    def disconnect(self, ws: WebSocket) -> None:
        """移除连接。"""
        self._connections.pop(ws, None)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """向所有连接广播 JSON 消息，忽略单个连接的发送失败。"""
        text = json.dumps(message, ensure_ascii=False, default=str)
        dead: list[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_text(text)
            except Exception as e:  # noqa: BLE001
                logger.debug("广播失败，移除连接: %s", e)
                dead.append(ws)
        for ws in dead:
            self._connections.pop(ws, None)

    @property
    def count(self) -> int:
        return len(self._connections)


# 全局 Hub 实例（行情 + 告警共用同一管理器，靠消息 type 区分）
quotes_hub = ConnectionManager()
alerts_hub = ConnectionManager()
