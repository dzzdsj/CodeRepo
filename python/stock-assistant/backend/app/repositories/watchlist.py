"""WatchlistItem 数据访问层。"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import WatchlistItem


class WatchlistRepository:
    """自选股条目数据访问对象。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[WatchlistItem]:
        """查询全部自选股，按 sort_order, id 排序。"""
        stmt = select(WatchlistItem).order_by(
            WatchlistItem.sort_order.asc(), WatchlistItem.id.asc()
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_codes(self) -> list[str]:
        """查询全部自选股 code（去重，供 monitor 拉取行情用）。"""
        stmt = select(WatchlistItem.code).distinct()
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def list_with_stock(self) -> list[tuple[WatchlistItem, str]]:
        """联表查询，返回 (WatchlistItem, stock.name) 列表。"""
        from app.models.stock import Stock

        stmt = (
            select(WatchlistItem, Stock.name)
            .outerjoin(Stock, WatchlistItem.code == Stock.code)
            .order_by(WatchlistItem.sort_order.asc(), WatchlistItem.id.asc())
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def add(
        self,
        code: str,
        group_name: str = "默认",
        note: str | None = None,
        sort_order: int = 0,
    ) -> WatchlistItem:
        """新增自选股条目。"""
        item = WatchlistItem(
            code=code,
            group_name=group_name,
            note=note,
            sort_order=sort_order,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def delete_by_code(self, code: str) -> int:
        """按 code 删除全部条目。返回删除行数。"""
        stmt = delete(WatchlistItem).where(WatchlistItem.code == code)
        result = await self.session.execute(stmt)
        return int(result.rowcount or 0)

    async def update_by_code(
        self,
        code: str,
        group_name: str | None = None,
        note: str | None = None,
        sort_order: int | None = None,
    ) -> list[WatchlistItem]:
        """按 code 更新所有匹配条目（P1 简化：一次更新全部匹配项）。"""
        stmt = select(WatchlistItem).where(WatchlistItem.code == code)
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        for item in items:
            if group_name is not None:
                item.group_name = group_name
            if note is not None:
                item.note = note
            if sort_order is not None:
                item.sort_order = sort_order
            self.session.add(item)
        await self.session.flush()
        return items

    async def count(self) -> int:
        """统计自选股条目数。"""
        from sqlalchemy import func

        result = await self.session.execute(select(func.count()).select_from(WatchlistItem))
        return int(result.scalar_one())


__all__ = ["WatchlistRepository"]
