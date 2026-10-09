"""预置股票库种子数据：知名 A 股 + 默认自选股。

首次启动时由 main.py 调用，将以下股票写入 stock 表，并预置默认自选股。
添加自选股时若 code 不在 stock 表中，watchlist 路由会自动通过 data_source
拉取该股票信息并写入 stock 表（无需手动刷新股票库）。
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import AlertRule
from app.models.stock import Stock
from app.models.watchlist import WatchlistItem

# 预置股票库（code, name, market, industry）
SEED_STOCKS: list[tuple[str, str, str, str]] = [
    # 沪市主板
    ("600519", "贵州茅台", "SH", "白酒"),
    ("601318", "中国平安", "SH", "保险"),
    ("600036", "招商银行", "SH", "银行"),
    ("601899", "紫金矿业", "SH", "有色"),
    ("600276", "恒瑞医药", "SH", "医药"),
    ("601012", "隆基绿能", "SH", "光伏"),
    ("600900", "长江电力", "SH", "电力"),
    ("601398", "工商银行", "SH", "银行"),
    ("600030", "中信证券", "SH", "证券"),
    ("601166", "兴业银行", "SH", "银行"),
    ("600028", "中国石化", "SH", "石油"),
    ("601857", "中国石油", "SH", "石油"),
    ("600809", "山西汾酒", "SH", "白酒"),
    ("600690", "海尔智家", "SH", "家电"),
    ("601888", "中国中免", "SH", "零售"),
    # 深市主板/创业板
    ("000858", "五粮液", "SZ", "白酒"),
    ("000333", "美的集团", "SZ", "家电"),
    ("000651", "格力电器", "SZ", "家电"),
    ("000001", "平安银行", "SZ", "银行"),
    ("000002", "万科A", "SZ", "地产"),
    ("000725", "京东方A", "SZ", "面板"),
    ("002594", "比亚迪", "SZ", "汽车"),
    ("002475", "立讯精密", "SZ", "电子"),
    ("002241", "歌尔股份", "SZ", "电子"),
    ("300750", "宁德时代", "SZ", "电池"),
    ("300059", "东方财富", "SZ", "证券"),
    ("300760", "迈瑞医疗", "SZ", "医疗器械"),
    ("300015", "爱尔眼科", "SZ", "医疗"),
    ("300498", "温氏股份", "SZ", "养殖"),
    ("002271", "东方雨虹", "SZ", "建材"),
    # 科创板
    ("688981", "中芯国际", "SH", "半导体"),
    ("688256", "寒武纪", "SH", "半导体"),
    ("688041", "海光信息", "SH", "半导体"),
    ("688303", "大全能源", "SH", "光伏"),
    ("688599", "天合光能", "SH", "光伏"),
]

# 默认自选股（从预置库中选 8 只作为初始自选）
DEFAULT_WATCHLIST: list[str] = [
    "600519",
    "601318",
    "300750",
    "000858",
    "002594",
    "300059",
    "688981",
    "600030",
]

# 大盘指数定义（code -> name, AkShare symbol）
INDEX_DEFS: list[dict[str, str]] = [
    {"code": "000001", "name": "上证指数", "symbol": "sh000001"},
    {"code": "399001", "name": "深证成指", "symbol": "sz399001"},
    {"code": "399006", "name": "创业板指", "symbol": "sz399006"},
    {"code": "000688", "name": "科创50", "symbol": "sh000688"},
    {"code": "000300", "name": "沪深300", "symbol": "sh000300"},
]

# 默认告警规则
DEFAULT_RULES: list[dict] = [
    {
        "id": "rule-change-pct-5",
        "name": "涨跌幅超5%",
        "enabled": True,
        "signal_type": "change_pct",
        "params": {"threshold": 5.0},
        "scope": {"codes": []},
        "session_start": "09:30",
        "session_end": "15:00",
        "channels": ["wechat", "web"],
        "cooldown_minutes": 30,
    },
    {
        "id": "rule-speed-3",
        "name": "5分钟涨速超3%",
        "enabled": True,
        "signal_type": "speed",
        "params": {"threshold": 3.0, "windowMinutes": 5},
        "scope": {"codes": []},
        "session_start": "09:30",
        "session_end": "15:00",
        "channels": ["wechat", "web"],
        "cooldown_minutes": 15,
    },
    {
        "id": "rule-volume-2",
        "name": "量比超2倍",
        "enabled": True,
        "signal_type": "volume",
        "params": {"threshold": 2.0, "volMultiple": 2.0},
        "scope": {"codes": []},
        "session_start": "09:30",
        "session_end": "15:00",
        "channels": ["web"],
        "cooldown_minutes": 30,
    },
]


async def seed_stocks(session: AsyncSession) -> int:
    """写入预置股票库（已存在则跳过），返回新增数量。"""
    existing_codes: set[str] = set()
    rows = await session.execute(select(Stock.code))
    for (code,) in rows.all():
        existing_codes.add(code)

    added = 0
    for code, name, market, industry in SEED_STOCKS:
        if code in existing_codes:
            continue
        session.add(Stock(code=code, name=name, market=market, industry=industry))
        added += 1
    if added:
        await session.flush()
    return added


async def seed_default_watchlist(session: AsyncSession) -> int:
    """写入默认自选股（已存在则跳过），返回新增数量。"""
    existing_codes: set[str] = set()
    rows = await session.execute(select(WatchlistItem.code))
    for (code,) in rows.all():
        existing_codes.add(code)

    added = 0
    for idx, code in enumerate(DEFAULT_WATCHLIST):
        if code in existing_codes:
            continue
        session.add(
            WatchlistItem(
                code=code,
                group_name="默认",
                note=None,
                sort_order=idx,
            )
        )
        added += 1
    if added:
        await session.flush()
    return added


async def seed_default_rules(session: AsyncSession) -> int:
    """写入默认告警规则（已存在则跳过），返回新增数量。"""
    existing_ids: set[str] = set()
    rows = await session.execute(select(AlertRule.id))
    for (rule_id,) in rows.all():
        existing_ids.add(rule_id)

    added = 0
    for rule_data in DEFAULT_RULES:
        if rule_data["id"] in existing_ids:
            continue
        session.add(
            AlertRule(
                id=rule_data["id"],
                name=rule_data["name"],
                enabled=rule_data["enabled"],
                signal_type=rule_data["signal_type"],
                params=json.dumps(rule_data["params"], ensure_ascii=False),
                scope=json.dumps(rule_data["scope"], ensure_ascii=False),
                session_start=rule_data["session_start"],
                session_end=rule_data["session_end"],
                channels=json.dumps(rule_data["channels"], ensure_ascii=False),
                cooldown_minutes=rule_data["cooldown_minutes"],
            )
        )
        added += 1
    if added:
        await session.flush()
    return added
