"""FastAPI 公共依赖。"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as _get_db


async def get_session() -> AsyncIterator[AsyncSession]:
    """数据库 Session 依赖（别名，便于后续扩展）。"""
    async for s in _get_db():
        yield s


SessionDep = Depends(get_session)
