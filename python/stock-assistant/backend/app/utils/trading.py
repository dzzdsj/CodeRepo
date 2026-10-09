"""交易时段与交易日工具。"""

from __future__ import annotations

from datetime import datetime, time

# A 股交易时段（含午间休市）
MORNING_START = time(9, 30)
MORNING_END = time(11, 30)
AFTERNOON_START = time(13, 0)
AFTERNOON_END = time(15, 0)


def is_trading_time(now: datetime | None = None) -> bool:
    """判断当前是否处于 A 股交易时段（含午休排除）。"""
    now = now or datetime.now()
    # 周末不交易
    if now.weekday() >= 5:
        return False
    t = now.time()
    if MORNING_START <= t <= MORNING_END:
        return True
    if AFTERNOON_START <= t <= AFTERNOON_END:
        return True
    return False


def is_trading_day(now: datetime | None = None) -> bool:
    """简单判断交易日（仅排除周末，不处理节假日）。"""
    now = now or datetime.now()
    return now.weekday() < 5
