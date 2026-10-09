"""Stock 数据访问层。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock


class StockRepository:
    """Stock 表数据访问对象。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_code(self, code: str) -> Stock | None:
        """按主键 code 查询。"""
        return await self.session.get(Stock, code)

    async def upsert(
        self,
        code: str,
        name: str,
        market: str = "SH",
        industry: str | None = None,
    ) -> Stock:
        """插入或忽略（P1 用 SQLite 的简单 select+insert 模式）。

        market 由调用方传入，data_source 知道 code 归属 SH/SZ。
        """
        existing = await self.get_by_code(code)
        if existing is not None:
            # 已存在则更新名称（akshare 名称偶尔变化），其它字段保持
            existing.name = name
            if market:
                existing.market = market
            if industry:
                existing.industry = industry
            self.session.add(existing)
            await self.session.flush()
            return existing
        stock = Stock(code=code, name=name, market=market, industry=industry)
        self.session.add(stock)
        await self.session.flush()
        return stock

    async def count(self) -> int:
        """统计股票表记录数（用于 system/status）。"""
        from sqlalchemy import func

        result = await self.session.execute(select(func.count()).select_from(Stock))
        return int(result.scalar_one())


__all__ = ["StockRepository"]
