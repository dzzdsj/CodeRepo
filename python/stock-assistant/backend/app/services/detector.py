"""告警检测引擎：对每条新行情执行规则匹配，命中则落库+推送。

四类信号检测：
1. change_pct  — 涨跌幅阈值：|changePct| >= threshold
2. speed       — 短时涨速异动：窗口内涨速 >= threshold
3. volume      — 成交量异动：量比 >= volMultiple（基于历史均量）
4. indicator   — 技术指标突破（P3 预留，暂返回不命中）
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.alert import Alert
from app.models.rule import AlertRule
from app.schemas.quote import Quote
from app.services.monitor import monitor
from app.ws.hub import alerts_hub

logger = logging.getLogger(__name__)

# 涨速计算最小数据量
_MIN_HISTORY_FOR_SPEED = 3


class AlertDetector:
    """告警检测引擎单例。"""

    def __init__(self) -> None:
        # 冷却表：(rule_id, code) -> 上次触发时间戳
        self._cooldowns: dict[tuple[str, str], float] = {}
        # 规则缓存
        self._rules: list[AlertRule] = []
        self._rules_ts: float = 0.0
        self._push_callback: Any = None  # 推送回调

    def set_push_callback(self, callback: Any) -> None:
        """注入推送回调函数（async def fn(alert: dict) -> bool）。"""
        self._push_callback = callback

    async def _ensure_rules(self) -> list[AlertRule]:
        """加载启用的规则（60 秒缓存）。"""
        now = time.time()
        if self._rules and (now - self._rules_ts < 60):
            return self._rules
        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(AlertRule).where(AlertRule.enabled.is_(True))
            )
            self._rules = list(rows.scalars().all())
        self._rules_ts = now
        return self._rules

    async def refresh_rules(self) -> None:
        """强制刷新规则缓存（规则变更后调用）。"""
        self._rules_ts = 0.0
        await self._ensure_rules()

    async def check_quotes(self, quotes: dict[str, Quote]) -> list[dict]:
        """对一批新行情执行所有规则匹配，返回触发的告警列表。

        Args:
            quotes: 本次拉取的行情 dict[code, Quote]

        Returns:
            触发的告警 dict 列表（含 code/ruleId/signalType/triggerValue/threshold/price/snapshot）
        """
        rules = await self._ensure_rules()
        if not rules or not quotes:
            return []

        triggered: list[dict] = []
        now_ts = time.time()

        for rule in rules:
            # 时段过滤
            if not self._in_session(rule.session_start, rule.session_end):
                continue

            scope_codes = self._parse_scope(rule.scope)
            params = json.loads(rule.params) if isinstance(rule.params, str) else rule.params
            threshold = float(params.get("threshold", 0))

            for code, quote in quotes.items():
                # 范围过滤
                if scope_codes and code not in scope_codes:
                    continue

                # 冷却检查
                key = (rule.id, code)
                last_ts = self._cooldowns.get(key, 0)
                if last_ts and (now_ts - last_ts < rule.cooldown_minutes * 60):
                    continue

                # 信号检测
                hit = self._detect(rule.signal_type, quote, params, threshold)
                if hit is None:
                    continue

                trigger_value, signal_desc = hit
                alert = {
                    "id": str(uuid.uuid4()),
                    "code": code,
                    "name": quote.name,
                    "ruleId": rule.id,
                    "ruleName": rule.name,
                    "signalType": rule.signal_type,
                    "triggerValue": trigger_value,
                    "threshold": threshold,
                    "price": quote.price,
                    "snapshot": self._build_snapshot(quote),
                    "desc": signal_desc,
                    "timestamp": datetime.now().isoformat(),
                }
                triggered.append(alert)
                self._cooldowns[key] = now_ts

        # 异步落库 + 推送
        if triggered:
            await self._persist_and_push(triggered)

        return triggered

    def _detect(
        self,
        signal_type: str,
        quote: Quote,
        params: dict,
        threshold: float,
    ) -> tuple[float, str] | None:
        """执行单条信号检测，返回 (触发值, 描述) 或 None。

        - change_pct: |涨跌幅| >= threshold
        - speed: 窗口内涨速 >= threshold
        - volume: 量比 >= volMultiple
        - indicator: 技术指标突破（MA金叉/MACD金叉/RSI超买超卖/KDJ超买超卖）
        """
        if signal_type == "change_pct":
            if abs(quote.changePct) >= threshold:
                direction = "大涨" if quote.changePct > 0 else "大跌"
                return abs(quote.changePct), f"{direction}{abs(quote.changePct):.2f}%"

        elif signal_type == "speed":
            window = int(params.get("windowMinutes", 5))
            speed = self._calc_speed(quote.code, window)
            if speed is not None and abs(speed) >= threshold:
                direction = "急涨" if speed > 0 else "急跌"
                return abs(speed), f"{window}分钟{direction}速{abs(speed):.2f}%"

        elif signal_type == "volume":
            vol_multiple = float(params.get("volMultiple", 2.0))
            ratio = self._calc_vol_ratio(quote.code, quote.volume)
            if ratio is not None and ratio >= vol_multiple:
                return ratio, f"量比{ratio:.1f}倍"

        elif signal_type == "indicator":
            return self._detect_indicator(quote, params, threshold)

        return None

    def _detect_indicator(
        self,
        quote: Quote,
        params: dict,
        threshold: float,
    ) -> tuple[float, str] | None:
        """技术指标突破检测。

        params.indicator 决定检测类型：
        - ma_golden_cross: MA5 上穿 MA10
        - macd_golden_cross: DIF 上穿 DEA
        - rsi_oversold: RSI 低于 threshold（超卖）
        - rsi_overbought: RSI 高于 threshold（超买）
        - kdj_oversold: KDJ 超卖（K < threshold）
        - kdj_overbought: KDJ 超买（K > threshold）
        """
        from app.services.indicators import get_indicator_signals

        indicator_type = params.get("indicator", "macd_golden_cross")
        history = monitor.get_history(quote.code)

        if len(history) < 20:
            return None

        signals = get_indicator_signals(history)
        if not signals:
            return None

        if indicator_type == "ma_golden_cross":
            ma = signals.get("ma", {})
            if ma.get("golden_cross"):
                ma5 = ma.get("ma5", 0) or 0
                ma10 = ma.get("ma10", 0) or 0
                return ma5 - ma10, f"MA5({ma5:.2f})上穿MA10({ma10:.2f})"

        elif indicator_type == "macd_golden_cross":
            macd = signals.get("macd", {})
            if macd.get("golden_cross"):
                dif = macd.get("dif", 0) or 0
                dea = macd.get("dea", 0) or 0
                return dif - dea, f"MACD金叉 DIF({dif:.4f})>DEA({dea:.4f})"

        elif indicator_type == "rsi_oversold":
            rsi = signals.get("rsi")
            if rsi is not None and rsi <= threshold:
                return rsi, f"RSI{rsi:.1f}低于{threshold}（超卖）"

        elif indicator_type == "rsi_overbought":
            rsi = signals.get("rsi")
            if rsi is not None and rsi >= threshold:
                return rsi, f"RSI{rsi:.1f}高于{threshold}（超买）"

        elif indicator_type == "kdj_oversold":
            kdj = signals.get("kdj", {})
            k = kdj.get("k")
            if k is not None and k <= threshold:
                return k, f"KDJ超卖 K({k:.1f})<{' '}{threshold}"

        elif indicator_type == "kdj_overbought":
            kdj = signals.get("kdj", {})
            k = kdj.get("k")
            if k is not None and k >= threshold:
                return k, f"KDJ超买 K({k:.1f})>{threshold}"

        return None

    def _calc_speed(self, code: str, window_minutes: int) -> float | None:
        """计算窗口内涨速（%）。"""
        history = monitor.get_history(code)
        if len(history) < _MIN_HISTORY_FOR_SPEED:
            return None
        # 取窗口内最近 N 条（假设 5 秒间隔，window 分钟约 window*12 条）
        n = min(len(history), window_minutes * 12)
        recent = history[-n:]
        if len(recent) < 2:
            return None
        first_price = recent[0].price
        last_price = recent[-1].price
        if first_price <= 0:
            return None
        return round((last_price - first_price) / first_price * 100, 2)

    def _calc_vol_ratio(self, code: str, current_vol: float) -> float | None:
        """计算量比：当前量 / 近 N 条均量。"""
        history = monitor.get_history(code)
        if len(history) < 5 or current_vol <= 0:
            return None
        # 排除最新一条（当前量）
        prev_vols = [q.volume for q in history[:-1] if q.volume > 0]
        if not prev_vols:
            return None
        avg_vol = sum(prev_vols) / len(prev_vols)
        if avg_vol <= 0:
            return None
        return round(current_vol / avg_vol, 2)

    def _build_snapshot(self, quote: Quote) -> dict:
        """构建行情快照。"""
        return {
            "price": quote.price,
            "changePct": quote.changePct,
            "changeAmt": quote.changeAmt,
            "volume": quote.volume,
            "amount": quote.amount,
            "high": quote.high,
            "low": quote.low,
            "open": quote.open,
            "preClose": quote.preClose,
            "timestamp": quote.timestamp,
        }

    def _in_session(self, start: str, end: str) -> bool:
        """判断当前时间是否在规则的生效时段内。"""
        now = datetime.now()
        current = now.strftime("%H:%M")
        return start <= current <= end

    def _parse_scope(self, scope_json: Any) -> list[str]:
        """解析规则 scope。"""
        if isinstance(scope_json, str):
            try:
                scope = json.loads(scope_json)
            except (json.JSONDecodeError, TypeError):
                return []
        elif isinstance(scope_json, dict):
            scope = scope_json
        else:
            return []
        codes = scope.get("codes")
        return codes if codes else []

    async def _persist_and_push(self, alerts: list[dict]) -> None:
        """告警落库 + WebSocket 推送 + 微信推送。"""
        async with AsyncSessionLocal() as session:
            for alert in alerts:
                # 落库
                db_alert = Alert(
                    id=alert["id"],
                    code=alert["code"],
                    rule_id=alert["ruleId"],
                    signal_type=alert["signalType"],
                    trigger_value=alert["triggerValue"],
                    threshold=alert["threshold"],
                    price=alert["price"],
                    snapshot=json.dumps(alert["snapshot"], ensure_ascii=False),
                    pushed=False,
                )
                session.add(db_alert)
            await session.commit()

        # WebSocket 实时推送
        for alert in alerts:
            await alerts_hub.broadcast({"type": "alert", "data": alert})

        # 微信推送
        if self._push_callback:
            for alert in alerts:
                try:
                    pushed = await self._push_callback(alert)
                    if pushed:
                        async with AsyncSessionLocal() as session:
                            db_alert = await session.get(Alert, alert["id"])
                            if db_alert:
                                db_alert.pushed = True
                                await session.commit()
                except Exception as e:  # noqa: BLE001
                    logger.error("推送告警失败 %s: %s", alert["code"], e)


# 全局单例
detector = AlertDetector()
