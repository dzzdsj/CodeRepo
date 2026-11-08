from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，唯一数据源为环境变量 / .env 文件，禁止在代码中硬编码密钥。"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # 应用
    app_name: str = "AIDevOps"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:5173"]

    # 数据库（默认 SQLite，零外部依赖即可启动；生产通过 DATABASE_URL 切换 PostgreSQL）
    database_url: str = "sqlite:///./aidevops.db"

    # JWT（生产环境必须通过环境变量注入 JWT_SECRET_KEY）
    jwt_secret_key: str = "dev-insecure-secret-please-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # RAG 知识库
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_top_k: int = 5


settings = Settings()
