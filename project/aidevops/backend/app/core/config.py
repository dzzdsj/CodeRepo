from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AIDevOps"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
