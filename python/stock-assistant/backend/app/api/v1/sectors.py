"""板块资金流向路由。"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.data_source import fetch_sector_fund_flow

router = APIRouter()


@router.get("/fund-flow")
async def get_sector_fund_flow(
    sector_type: str = Query("industry", description="板块类型: industry=行业, concept=概念"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
) -> dict:
    """获取板块资金流向排名。"""
    data = await fetch_sector_fund_flow(sector_type=sector_type, limit=limit)
    return {"sectorType": sector_type, "data": data}
