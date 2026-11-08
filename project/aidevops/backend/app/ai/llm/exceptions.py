"""LLM 调用相关异常。"""


class LLMError(Exception):
    """大模型调用失败。"""


class LLMTimeoutError(LLMError):
    """大模型调用超时。"""
