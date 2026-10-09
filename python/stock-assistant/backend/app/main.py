"""FastAPI 应用入口。

职责：
1. 创建数据库表（首次启动）
2. 写入预置股票库与默认自选股
3. 启动 MonitorService 调度器
4. 挂载 REST API 与 WebSocket
5. 关闭时停止调度器
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.services.detector import detector
from app.services.monitor import monitor
from app.services.push import pusher
from app.services.seed import seed_default_rules, seed_default_watchlist, seed_stocks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def _auto_migrate(conn) -> None:
    """SQLite 自动补列：检查并添加新字段。"""
    from sqlalchemy import text

    migrations = [
        ("alert", "ai_analysis", "TEXT"),
        ("alert", "ai_analyzed_at", "DATETIME"),
    ]
    for table, column, coltype in migrations:
        try:
            cols = await conn.execute(text(f"PRAGMA table_info({table})"))
            col_names = {row[1] for row in cols}
            if column not in col_names:
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"))
                logger.info("迁移：%s.%s 已添加", table, column)
        except Exception as e:  # noqa: BLE001
            logger.debug("迁移 %s.%s 跳过: %s", table, column, e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动与关闭钩子。"""
    # 启动
    logger.info("=== 股票助手启动 ===")
    # 1. 建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 1b. 自动迁移：给已有表补列（SQLite ALTER TABLE ADD COLUMN）
    async with engine.begin() as conn:
        await _auto_migrate(conn)
    logger.info("数据库表已就绪: %s", settings.sqlite_path)
    # 2. 种子数据
    async with AsyncSessionLocal() as session:
        added_stocks = await seed_stocks(session)
        added_watch = await seed_default_watchlist(session)
        added_rules = await seed_default_rules(session)
        await session.commit()
        logger.info("种子数据：股票 +%d，自选股 +%d，规则 +%d", added_stocks, added_watch, added_rules)
    # 3. 注入推送回调 + 启动调度
    detector.set_push_callback(pusher.send_alert)
    await detector.refresh_rules()
    await monitor.refresh_codes()
    await monitor.start()
    logger.info("MonitorService 已启动")
    # 4. 强制拉取一次行情填充缓存（非交易时段展示收盘数据）
    await monitor.force_fetch()
    yield
    # 关闭
    await monitor.stop()
    logger.info("=== 股票助手关闭 ===")


app = FastAPI(
    title="股票助手 API",
    version="0.1.0",
    description="A 股实时行情监控与智能告警平台",
    lifespan=lifespan,
)

# CORS（前端 dev 跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API
app.include_router(api_router, prefix="/api")

# WebSocket 路由（独立挂载，便于与 REST 区分）
# quotes ws 已在 api_router 内：/api/quotes/ws


@app.get("/")
async def root() -> dict:
    return {"service": "stock-assistant", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "monitor": monitor.get_status()}
