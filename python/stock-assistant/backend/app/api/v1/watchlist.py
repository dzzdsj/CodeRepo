"""自选股 CRUD 路由。"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.stock import Stock
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistCreate, WatchlistItemOut, WatchlistUpdate
from app.services import data_source
from app.services.monitor import monitor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[WatchlistItemOut])
async def list_watchlist(session: AsyncSession = Depends(get_session)) -> list[WatchlistItemOut]:
    """获取自选股列表（含股票名称，按分组+排序顺序）。"""
    stmt = (
        select(WatchlistItem, Stock.name)
        .join(Stock, WatchlistItem.code == Stock.code)
        .order_by(WatchlistItem.group_name, WatchlistItem.sort_order)
    )
    rows = await session.execute(stmt)
    out: list[WatchlistItemOut] = []
    for item, name in rows.all():
        out.append(
            WatchlistItemOut(
                id=item.id,
                code=item.code,
                name=name,
                groupName=item.group_name,
                note=item.note,
                sortOrder=item.sort_order,
            )
        )
    return out


async def _ensure_stock(session: AsyncSession, code: str) -> Stock | None:
    """确保 stock 表存在该 code，不存在则从数据源补全写入。"""
    stock = await session.get(Stock, code)
    if stock:
        return stock

    # 通过数据源精确匹配（腾讯/AkShare 任一返回即可）
    try:
        candidates = await data_source.search_stocks(code, limit=20)
    except Exception as e:  # noqa: BLE001
        logger.warning("补全股票 %s 时数据源调用失败: %s", code, e)
        return None

    for c in candidates:
        if c.get("code") == code:
            stock = Stock(
                code=code,
                name=c.get("name") or code,
                market=c.get("market") or ("SH" if code.startswith(("6", "9")) else "SZ"),
                industry=c.get("industry") or None,
            )
            session.add(stock)
            try:
                await session.flush()
            except IntegrityError:
                await session.rollback()
                return await session.get(Stock, code)
            logger.info("自动补全股票库: %s %s", code, stock.name)
            return stock
    return None


@router.post("", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
async def add_watchlist(
    payload: WatchlistCreate,
    session: AsyncSession = Depends(get_session),
) -> WatchlistItemOut:
    """添加自选股。stock 表无该 code 时自动从数据源补全。"""
    code = payload.code.strip()
    stock = await _ensure_stock(session, code)
    if not stock:
        raise HTTPException(status_code=404, detail=f"股票 {code} 不存在")

    # 计算同组下一个排序序号
    stmt = select(WatchlistItem.sort_order).where(WatchlistItem.group_name == payload.groupName)
    existing = (await session.execute(stmt)).all()
    next_order = max((r[0] for r in existing), default=-1) + 1

    item = WatchlistItem(
        code=code,
        group_name=payload.groupName,
        note=payload.note,
        sort_order=next_order,
    )
    session.add(item)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"{code} 已在自选股中") from None

    await session.refresh(item)
    # 通知 monitor 刷新自选股 codes
    await monitor.refresh_codes()
    # 立即拉取新增股票行情并广播（非交易时段也能展示收盘数据）
    await monitor.fetch_for_code(code)
    return WatchlistItemOut(
        id=item.id,
        code=item.code,
        name=stock.name,
        groupName=item.group_name,
        note=item.note,
        sortOrder=item.sort_order,
    )


@router.put("/{code}", response_model=WatchlistItemOut)
async def update_watchlist(
    code: str,
    payload: WatchlistUpdate,
    session: AsyncSession = Depends(get_session),
) -> WatchlistItemOut:
    """编辑自选股（分组/备注）。"""
    stmt = (
        select(WatchlistItem)
        .where(WatchlistItem.code == code)
        .order_by(WatchlistItem.id.desc())
        .limit(1)
    )
    item = (await session.execute(stmt)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail=f"自选股 {code} 不存在")

    if payload.groupName is not None:
        item.group_name = payload.groupName
    if payload.note is not None:
        item.note = payload.note
    await session.flush()
    await session.refresh(item)

    stock = await session.get(Stock, code)
    return WatchlistItemOut(
        id=item.id,
        code=item.code,
        name=stock.name if stock else "",
        groupName=item.group_name,
        note=item.note,
        sortOrder=item.sort_order,
    )


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(code: str, session: AsyncSession = Depends(get_session)) -> None:
    """删除自选股（删除该 code 的所有分组记录）。"""
    stmt = select(WatchlistItem).where(WatchlistItem.code == code)
    rows = (await session.execute(stmt)).scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"自选股 {code} 不存在")
    for r in rows:
        await session.delete(r)
    await monitor.refresh_codes()
