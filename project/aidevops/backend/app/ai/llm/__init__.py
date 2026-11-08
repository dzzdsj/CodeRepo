"""LLM 适配层：多模型接入，统一 OpenAI 兼容协议。"""
from app.ai.llm.client import LLMClient, ChatMessage, ChatResult
from app.ai.llm.embedding import EmbeddingClient

__all__ = ["LLMClient", "ChatMessage", "ChatResult", "EmbeddingClient"]
