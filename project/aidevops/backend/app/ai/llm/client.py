"""LLM 适配客户端。

当前统一采用 OpenAI 兼容协议（/v1/chat/completions），可覆盖 OpenAI、
DeepSeek、通义千问、智谱 GLM、Ollama、vLLM 等绝大多数模型服务。
后续如需接入私有非兼容协议，可在 LLMClient 中按 provider 分支扩展。
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

import httpx

from app.ai.llm.exceptions import LLMError, LLMTimeoutError


@dataclass
class ChatMessage:
    role: str  # system / user / assistant
    content: str


@dataclass
class ChatResult:
    content: str
    model: str
    usage: dict | None = None
    latency_ms: int = 0


class LLMClient:
    """OpenAI 兼容协议的 LLM 客户端。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def chat(
        self,
        messages: Iterable[ChatMessage] | Iterable[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResult:
        payload: dict = {
            "model": self.model,
            "messages": [
                m if isinstance(m, dict) else {"role": m.role, "content": m.content}
                for m in messages
            ],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        start = time.perf_counter()
        try:
            resp = self._http.post("/v1/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("请求大模型超时") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"网络错误: {exc}") from exc
        latency_ms = int((time.perf_counter() - start) * 1000)

        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except ValueError:
                detail = resp.text
            raise LLMError(f"模型服务返回错误({resp.status_code}): {detail}")

        data = resp.json()
        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage")
            model = data.get("model", self.model)
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"模型响应解析失败: {data}") from exc

        return ChatResult(
            content=content,
            model=model,
            usage=usage,
            latency_ms=latency_ms,
        )

    def test_connection(self) -> ChatResult:
        """用一条极短的请求验证连通性，返回首包延迟与响应。"""
        return self.chat(
            [ChatMessage(role="user", content="只回复: ok")],
            temperature=0.0,
            max_tokens=16,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "LLMClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
