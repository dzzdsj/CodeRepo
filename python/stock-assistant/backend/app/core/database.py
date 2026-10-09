"""SQLAlchemy 异步引擎与 Session。"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 确保 SQLite 数据目录存在（触发 sqlite_path 属性创建目录），并使用绝对路径
_db_path = settings.sqlite_path
# 构造绝对路径 URL，避免依赖运行时 cwd
_db_url = f"sqlite+aiosqlite:///{_db_path}"

# SQLite 默认 check_same_thread=False；async 引擎
engine = create_async_engine(
    _db_url,
    echo=settings.app_debug and False,  # 调试时可手动改为 True
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：提供异步数据库 Session。"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
