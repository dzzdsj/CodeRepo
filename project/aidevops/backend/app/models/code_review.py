from sqlalchemy import Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class CodeReview(TimestampMixin, Base):
    """AI 代码审查记录。"""

    __tablename__ = "code_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repo: Mapped[str] = mapped_column(String(256), index=True)
    branch: Mapped[str | None] = mapped_column(String(128), nullable=True)
    commit: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    language: Mapped[str] = mapped_column(String(32), default="text", nullable=False)
    code_content: Mapped[str] = mapped_column(Text)
    # pending / completed / failed
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 结构化审查结果：{summary, issues: [{severity, category, line, description, suggestion}]} 或 {error}
    ai_suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
