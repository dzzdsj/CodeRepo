"""系统设置 Pydantic 模型：推送配置、调度配置。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PushConfigOut(BaseModel):
    """推送配置响应。"""

    provider: str = Field(description="serverchan | pushplus")
    enabled: bool
    hasToken: bool = Field(description="是否已配置 Token（不返回明文）")


class PushConfigUpdate(BaseModel):
    """更新推送配置。"""

    provider: str = "serverchan"
    token: str = Field(default="", description="明文 Token，空串表示不修改")
    enabled: bool = True


class SchedulerConfigOut(BaseModel):
    """调度配置响应。"""

    dataSource: str
    intervalSeconds: int
    sessionStart: str
    sessionEnd: str


class SchedulerConfigUpdate(BaseModel):
    """更新调度配置。"""

    dataSource: str | None = None
    intervalSeconds: int | None = None
    sessionStart: str | None = None
    sessionEnd: str | None = None


class PushTestResult(BaseModel):
    """测试推送结果。"""

    success: bool
    message: str
