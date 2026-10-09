"""系统配置 ORM：推送渠道、调度配置（单行配置）。"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PushConfig(Base):
    """推送渠道配置（单行：provider 决定唯一）。"""

    __tablename__ = "push_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # serverchan | pushplus
    token_encrypted: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SchedulerConfig(Base):
    """调度配置（单行，id 固定为 1）。"""

    __tablename__ = "scheduler_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    data_source: Mapped[str] = mapped_column(String(32), default="akshare", nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    session_start: Mapped[str] = mapped_column(String(5), default="09:30", nullable=False)
    session_end: Mapped[str] = mapped_column(String(5), default="15:00", nullable=False)


class AiConfig(Base):
    """AI 模型配置（单行，id 固定为 1）。"""

    __tablename__ = "ai_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    provider: Mapped[str] = mapped_column(String(32), default="zhipu", nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    base_url: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(64), default="glm-4-flash", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
