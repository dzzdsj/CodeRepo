"""应用配置：基于 pydantic-settings，从环境变量 / .env 加载。"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# 后端根目录：backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 应用
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./data/stock.db"

    # 加密密钥
    secret_key: str = "change-me-to-a-random-32-char-string"

    # 默认调度配置
    scheduler_interval_seconds: int = 5
    scheduler_session_start: str = "09:30"
    scheduler_session_end: str = "15:00"

    # 数据源
    data_source: Literal["akshare", "tushare"] = "akshare"
    tushare_token: str = ""

    # CORS：前端 dev 地址
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def sqlite_path(self) -> Path:
        """从 database_url 解析 SQLite 文件路径，确保目录存在。"""
        url = self.database_url
        # 形如 sqlite+aiosqlite:///./data/stock.db
        if ":///" in url:
            path_part = url.split(":///", 1)[1]
        else:
            path_part = "data/stock.db"
        path = Path(path_part)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
