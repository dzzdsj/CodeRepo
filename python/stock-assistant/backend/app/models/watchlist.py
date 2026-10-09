"""自选股 ORM。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_item"
    __table_args__ = (Index("idx_watchlist_code", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), ForeignKey("stock.code"), nullable=False)
    group_name: Mapped[str] = mapped_column(String(64), default="默认", nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WatchlistItem {self.code}>"
