"""Embedding 客户端：调用 OpenAI 兼容的 /v1/embeddings 端点。

与 LLMClient 共享 base_url / api_key，仅端点和请求体不同。
"""
from __future__ import annotations

import time
from typing import Iterable

import httpx

from app.ai.llm.exceptions import LLMError, LLMTimeoutError


class EmbeddingClient:
    """OpenAI 兼容协议的 Embedding 客户端。"""

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

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        """批量生成向量。"""
        input_texts = list(texts)
        if not input_texts:
            return []

        payload = {"model": self.model, "input": input_texts}
        start = time.perf_counter()
        try:
            resp = self._http.post("/v1/embeddings", json=payload)
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("请求 Embedding 超时") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"网络错误: {exc}") from exc
        _ = int((time.perf_counter() - start) * 1000)

        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except ValueError:
                detail = resp.text
            raise LLMError(f"Embedding 服务返回错误({resp.status_code}): {detail}")

        data = resp.json()
        try:
            embeddings = [item["embedding"] for item in data["data"]]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Embedding 响应解析失败: {data}") from exc

        return embeddings

    def embed_one(self, text: str) -> list[float]:
        """单条文本生成向量。"""
        return self.embed([text])[0]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "EmbeddingClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
