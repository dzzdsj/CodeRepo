import re

from sqlalchemy import Boolean, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def extract_variables(content: str) -> list[str]:
    """从模板内容中提取 {{var}} 占位符变量名，按出现顺序去重。"""
    seen: list[str] = []
    for m in VAR_PATTERN.findall(content):
        if m not in seen:
            seen.append(m)
    return seen


class PromptTemplate(TimestampMixin, Base):
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    variables: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    def render(self, values: dict[str, str]) -> str:
        """按提供的变量值渲染模板，未提供的变量保留占位符。"""
        def repl(m: re.Match) -> str:
            return values.get(m.group(1), m.group(0))
        return VAR_PATTERN.sub(repl, self.content)
