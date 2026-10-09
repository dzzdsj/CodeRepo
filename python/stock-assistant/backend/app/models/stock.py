"""股票基础库 ORM。"""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Stock(Base):
    __tablename__ = "stock"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)  # 600519
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    market: Mapped[str] = mapped_column(String(4), nullable=False)  # SH / SZ
    industry: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Stock {self.code} {self.name}>"
