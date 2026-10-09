"""告警规则 ORM（P2 使用，P1 提前建表）。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rule"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # uuid
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    scope: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    session_start: Mapped[str] = mapped_column(String(5), nullable=False, default="09:30")
    session_end: Mapped[str] = mapped_column(String(5), nullable=False, default="15:00")
    channels: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
