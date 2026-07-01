from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Xuan Agent"
    app_env: str = "development"
    api_prefix: str = "/api"

    database_url: str = "sqlite:///./xuan_agent.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"

    workspace_root: Path = Path("./workspace")
    sandbox_image: str = "xuan-agent-python-sandbox:latest"
    sandbox_timeout_seconds: int = 10
    sandbox_memory: str = "512m"
    sandbox_cpus: str = "1"

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
