from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class LlmModelBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    provider: str = Field(min_length=1, max_length=32)
    base_url: str = Field(min_length=1, max_length=256)
    api_key: str = Field(min_length=1, max_length=512)
    model: str = Field(min_length=1, max_length=128)
    is_default: bool = False
    is_enabled: bool = True
    remark: str | None = None


class LlmModelCreate(LlmModelBase):
    pass


class LlmModelUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    provider: str | None = Field(default=None, max_length=32)
    base_url: str | None = Field(default=None, max_length=256)
    # 空字符串表示不修改原密钥；非空字符串则替换
    api_key: str | None = Field(default=None, max_length=512)
    model: str | None = Field(default=None, max_length=128)
    is_default: bool | None = None
    is_enabled: bool | None = None
    remark: str | None = None


class LlmModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    base_url: str
    # 输出时仅保留密钥末尾 4 位，避免泄露
    api_key: str
    model: str
    is_default: bool
    is_enabled: bool
    remark: str | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("api_key")
    def _mask_api_key(self, v: str) -> str:
        if not v:
            return ""
        if len(v) <= 4:
            return "****"
        return f"****{v[-4:]}"


class LlmModelTestRequest(BaseModel):
    """未保存的模型配置连通性测试。"""

    base_url: str
    api_key: str
    model: str


class LlmModelTestResponse(BaseModel):
    ok: bool
    latency_ms: int
    message: str
