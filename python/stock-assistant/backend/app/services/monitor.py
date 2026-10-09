"""监控调度服务：APScheduler 定时拉取行情，更新内存缓存，广播 WebSocket。

- 行情缓存：进程内 dict[code, Quote]，最近 N 条环形缓冲（供涨速计算）
- 指数缓存：dict[code, IndexQuote]
- 自选股 codes 缓存：30 秒从 DB 刷新一次
- 调度：AsyncIOScheduler，个股行情 interval 秒、指数 10 秒
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.watchlist import WatchlistItem
from app.schemas.quote import IndexQuote, Quote
from app.services import data_source
from app.utils.trading import is_trading_time
from app.ws.hub import quotes_hub

logger = logging.getLogger(__name__)

# 行情历史缓冲长度（保留最近 N 条用于涨速/量能/技术指标计算）
_HISTORY_LEN = 500


class MonitorService:
    """全局监控调度服务单例。"""

    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler | None = None
        # 最新行情缓存
        self._quote_cache: dict[str, Quote] = {}
        # 历史行情环形缓冲：code -> list[Quote]
        self._quote_history: dict[str, list[Quote]] = {}
        # 指数缓存
        self._index_cache: list[IndexQuote] = []
        # 自选股 codes 缓存
        self._codes: list[str] = []
        self._codes_ts: float = 0.0
        # 最近一次采集耗时与状态
        self._last_fetch_at: float = 0.0
        self._last_fetch_ok: bool = False
        self._last_error: str = ""
        self._started = False

    # ---------- 生命周期 ----------

    async def start(self) -> None:
        """启动调度器（幂等）。"""
        if self._started:
            return
        self._scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        interval = settings.scheduler_interval_seconds
        # 个股行情任务
        self._scheduler.add_job(
            self._tick_quotes,
            trigger="interval",
            seconds=interval,
            id="fetch_quotes",
            max_instances=1,
            coalesce=True,
        )
        # 指数任务（10 秒）
        self._scheduler.add_job(
            self._tick_indexes,
            trigger="interval",
            seconds=10,
            id="fetch_indexes",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        self._started = True
        logger.info("MonitorService 启动，个股间隔=%ss，指数间隔=10s", interval)

    async def force_fetch(self) -> None:
        """强制拉取一次行情与指数（忽略交易时段，用于启动时填充缓存展示收盘数据）。"""
        codes = await self._ensure_codes()
        if codes:
            try:
                quotes = await asyncio.wait_for(
                    data_source.fetch_realtime_quotes(codes), timeout=60
                )
                if quotes:
                    self._update_cache(quotes)
                    self._last_fetch_ok = True
                    self._last_fetch_at = time.time()
                    logger.info("强制采集行情：%d 只", len(quotes))
            except asyncio.TimeoutError:
                logger.error("强制采集行情超时（60s）")
            except Exception as e:  # noqa: BLE001
                logger.error("强制采集行情失败: %s", e)
        try:
            indexes = await asyncio.wait_for(
                data_source.fetch_realtime_indexes(), timeout=30
            )
            if indexes:
                self._index_cache = indexes
                logger.info("强制采集指数：%d 只", len(indexes))
        except asyncio.TimeoutError:
            logger.error("强制采集指数超时（30s）")
        except Exception as e:  # noqa: BLE001
            logger.error("强制采集指数失败: %s", e)

    async def stop(self) -> None:
        """停止调度器。"""
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        self._started = False

    # ---------- 缓存读取 ----------

    def get_quotes(self, codes: list[str] | None = None) -> list[Quote]:
        """读取缓存行情；codes 为空返回全部。"""
        if codes is None:
            return list(self._quote_cache.values())
        return [self._quote_cache[c] for c in codes if c in self._quote_cache]

    def get_indexes(self) -> list[IndexQuote]:
        return list(self._index_cache)

    def get_history(self, code: str) -> list[Quote]:
        """返回指定股票的历史行情缓冲（最近 N 条）。"""
        return list(self._quote_history.get(code, []))

    def get_status(self) -> dict[str, Any]:
        return {
            "started": self._started,
            "watchlistCount": len(self._codes),
            "cacheCount": len(self._quote_cache),
            "indexCount": len(self._index_cache),
            "lastFetchAt": self._last_fetch_at,
            "lastFetchOk": self._last_fetch_ok,
            "lastError": self._last_error,
            "isTradingTime": is_trading_time(),
            "intervalSeconds": settings.scheduler_interval_seconds,
        }

    async def fetch_for_code(self, code: str) -> Quote | None:
        """立即拉取单个股票行情，更新缓存并广播（用于添加自选股后即时展示）。

        不依赖交易时段，确保用户新增自选股后立即可见价格（收盘数据）。
        """
        try:
            quotes = await asyncio.wait_for(
                data_source.fetch_realtime_quotes([code]), timeout=15
            )
        except asyncio.TimeoutError:
            logger.error("单股行情采集超时 code=%s", code)
            return None
        except Exception as e:  # noqa: BLE001
            logger.error("单股行情采集失败 code=%s: %s", code, e)
            return None

        if not quotes or code not in quotes:
            logger.warning("单股行情返回空 code=%s", code)
            return None

        quote = quotes[code]
        self._quote_cache[code] = quote
        history = self._quote_history.setdefault(code, [])
        history.append(quote)
        if len(history) > _HISTORY_LEN:
            del history[: len(history) - _HISTORY_LEN]

        await self._broadcast_quotes([quote])
        logger.info("单股行情已拉取并广播: %s %.2f", code, quote.price)
        return quote

    async def refresh_codes(self) -> list[str]:
        """从 DB 刷新自选股 codes（强制刷新，供 watchlist 变更后调用）。"""
        async with AsyncSessionLocal() as session:
            rows = await session.execute(select(WatchlistItem.code).order_by(WatchlistItem.sort_order))
            codes = [c for (c,) in rows.all()]
        self._codes = codes
        self._codes_ts = time.time()
        logger.info("自选股刷新：%d 只", len(codes))
        return codes

    async def _ensure_codes(self) -> list[str]:
        """确保 codes 缓存有效（30 秒过期则刷新）。"""
        if not self._codes or (time.time() - self._codes_ts > 30):
            await self.refresh_codes()
        return self._codes

    # ---------- 调度任务 ----------

    async def _tick_quotes(self) -> None:
        """个股行情采集任务。"""
        codes = await self._ensure_codes()
        if not codes:
            return
        # 非交易时段：跳过采集，但保留缓存（前端仍可看最后行情）
        if not is_trading_time():
            return
        t0 = time.time()
        try:
            quotes = await data_source.fetch_realtime_quotes(codes)
            self._last_fetch_at = t0
            self._last_fetch_ok = True
            self._last_error = ""
            if quotes:
                self._update_cache(quotes)
                await self._broadcast_quotes(list(quotes.values()))
                # 告警检测
                await self._run_detection(quotes)
        except Exception as e:  # noqa: BLE001
            self._last_fetch_ok = False
            self._last_error = str(e)
            logger.error("行情采集失败: %s", e)

    async def _tick_indexes(self) -> None:
        """指数行情采集任务。"""
        if not is_trading_time():
            return
        try:
            indexes = await data_source.fetch_realtime_indexes()
            if indexes:
                self._index_cache = indexes
                await self._broadcast_indexes(indexes)
        except Exception as e:  # noqa: BLE001
            logger.error("指数采集失败: %s", e)

    # ---------- 缓存更新与广播 ----------

    def _update_cache(self, quotes: dict[str, Quote]) -> None:
        """更新行情缓存与历史缓冲。"""
        for code, quote in quotes.items():
            self._quote_cache[code] = quote
            history = self._quote_history.setdefault(code, [])
            history.append(quote)
            if len(history) > _HISTORY_LEN:
                # 截断到最近 N 条
                del history[: len(history) - _HISTORY_LEN]

    async def _broadcast_quotes(self, quotes: list[Quote]) -> None:
        """广播行情到 WebSocket 订阅者。"""
        if not quotes:
            return
        await quotes_hub.broadcast(
            {
                "type": "quotes",
                "data": [q.model_dump() for q in quotes],
            }
        )

    async def _broadcast_indexes(self, indexes: list[IndexQuote]) -> None:
        await quotes_hub.broadcast(
            {
                "type": "indexes",
                "data": [i.model_dump() for i in indexes],
            }
        )

    async def _run_detection(self, quotes: dict[str, Quote]) -> None:
        """执行告警检测（延迟导入避免循环依赖）。"""
        try:
            from app.services.detector import detector
            await detector.check_quotes(quotes)
        except Exception as e:  # noqa: BLE001
            logger.error("告警检测失败: %s", e)


# 全局单例
monitor = MonitorService()
