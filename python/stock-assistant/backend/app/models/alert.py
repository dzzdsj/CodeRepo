"""告警记录 ORM（P2 使用，P1 提前建表）。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alert"
    __table_args__ = (
        Index("idx_alert_code_time", "code", "timestamp"),
        Index("idx_alert_time", "timestamp"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(16), ForeignKey("stock.code"), nullable=False)
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("alert_rule.id"), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    trigger_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    pushed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    # P3: AI 分析结果（JSON，含解读、操作建议、风险提示）
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
