"""技术指标计算模块：基于内存行情历史缓冲计算 MA/MACD/RSI/KDJ。

数据来源：monitor.get_history(code) 返回的 list[Quote]，按时间正序排列。
"""

from __future__ import annotations

from typing import Any

from app.schemas.quote import Quote


def calc_ma(prices: list[float], period: int) -> float | None:
    """简单移动平均。"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calc_ema(prices: list[float], period: int) -> float | None:
    """指数移动平均。"""
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema


def calc_macd(
    prices: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict[str, float | None] | None:
    """计算 MACD：DIF, DEA, MACD 柱。

    Returns:
        {"dif": float, "dea": float, "macd": float} 或 None
    """
    if len(prices) < slow + signal:
        return None

    # 计算 EMA 序列
    ema_fast_list: list[float] = []
    ema_slow_list: list[float] = []
    k_fast = 2 / (fast + 1)
    k_slow = 2 / (slow + 1)

    ema_fast = prices[0]
    ema_slow = prices[0]
    for p in prices[1:]:
        ema_fast = p * k_fast + ema_fast * (1 - k_fast)
        ema_slow = p * k_slow + ema_slow * (1 - k_slow)
        ema_fast_list.append(ema_fast)
        ema_slow_list.append(ema_slow)

    # DIF 序列 = EMA_fast - EMA_slow
    dif_list = [f - s for f, s in zip(ema_fast_list, ema_slow_list)]

    # DEA = DIF 的 EMA(signal)
    if len(dif_list) < signal:
        return None
    k_signal = 2 / (signal + 1)
    dea = dif_list[0]
    for d in dif_list[1:]:
        dea = d * k_signal + dea * (1 - k_signal)

    dif = dif_list[-1]
    macd_bar = (dif - dea) * 2  # MACD 柱 = (DIF - DEA) * 2

    return {"dif": dif, "dea": dea, "macd": macd_bar}


def calc_rsi(prices: list[float], period: int = 14) -> float | None:
    """计算 RSI。"""
    if len(prices) < period + 1:
        return None

    gains = []
    losses = []
    for i in range(-period, 0):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_kdj(
    history: list[Quote],
    period: int = 9,
) -> dict[str, float] | None:
    """计算 KDJ 指标。

    Args:
        history: 行情历史（按时间正序）
        period: 计算周期

    Returns:
        {"k": float, "d": float, "j": float} 或 None
    """
    if len(history) < period:
        return None

    k = 50.0
    d = 50.0

    for i in range(period - 1, len(history)):
        window = history[max(0, i - period + 1) : i + 1]
        highs = [q.high for q in window if q.high > 0]
        lows = [q.low for q in window if q.low > 0]
        if not highs or not lows:
            continue
        highest = max(highs)
        lowest = min(lows)
        close = history[i].price

        if highest == lowest:
            rsv = 50.0
        else:
            rsv = (close - lowest) / (highest - lowest) * 100

        k = 2 / 3 * k + 1 / 3 * rsv
        d = 2 / 3 * d + 1 / 3 * k

    j = 3 * k - 2 * d
    return {"k": round(k, 2), "d": round(d, 2), "j": round(j, 2)}


def get_indicator_signals(history: list[Quote]) -> dict[str, Any]:
    """计算全部技术指标信号。

    Returns:
        {
            "ma": {"ma5": float, "ma10": float, "ma20": float, "golden_cross": bool},
            "macd": {"dif": float, "dea": float, "macd": float, "golden_cross": bool},
            "rsi": float,
            "kdj": {"k": float, "d": float, "j": float, "oversold": bool, "overbought": bool},
        }
    """
    prices = [q.price for q in history if q.price > 0]
    result: dict[str, Any] = {}

    if len(prices) < 5:
        return result

    # MA
    ma5 = calc_ma(prices, 5)
    ma10 = calc_ma(prices, 10)
    ma20 = calc_ma(prices, 20)
    ma_golden_cross = None
    if ma5 is not None and ma10 is not None:
        ma_golden_cross = ma5 > ma10  # MA5 上穿 MA10
    result["ma"] = {
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "golden_cross": ma_golden_cross,
    }

    # MACD
    macd = calc_macd(prices)
    if macd:
        result["macd"] = {
            "dif": round(macd["dif"], 4),
            "dea": round(macd["dea"], 4),
            "macd": round(macd["macd"], 4),
            "golden_cross": macd["dif"] > macd["dea"],  # DIF 上穿 DEA
        }

    # RSI
    rsi = calc_rsi(prices)
    if rsi is not None:
        result["rsi"] = round(rsi, 2)

    # KDJ
    kdj = calc_kdj(history)
    if kdj:
        result["kdj"] = {
            "k": kdj["k"],
            "d": kdj["d"],
            "j": kdj["j"],
            "oversold": kdj["j"] < 0 or kdj["k"] < 20,  # 超卖
            "overbought": kdj["j"] > 100 or kdj["k"] > 80,  # 超买
        }

    return result
