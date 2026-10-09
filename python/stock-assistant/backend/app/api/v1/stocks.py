"""股票模糊搜索路由。"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services import data_source

router = APIRouter()


@router.get("/search")
async def search_stocks(q: str = Query(..., min_length=1, description="代码或名称关键字")) -> list[dict]:
    """模糊搜索 A 股（代码/名称）。数据来自 AkShare stock_info_a_code_name。"""
    return await data_source.search_stocks(q)
