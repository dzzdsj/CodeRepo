from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class LlmModel(TimestampMixin, Base):
    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(32))
    base_url: Mapped[str] = mapped_column(String(256))
    api_key: Mapped[str] = mapped_column(String(512))
    model: Mapped[str] = mapped_column(String(128))
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
