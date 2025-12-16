from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = BASE_DIR / "config.yaml"


def load_yaml_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class AppConfig(BaseModel):
    name: str = "PonnyExpres 2.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    host: str = "postgres"
    port: int = 5432
    user: str = "pony_user"
    password: str = "pony_password"
    name: str = "pony_db"


class RedisConfig(BaseModel):
    host: str = "redis"
    port: int = 6379
    db: int = 0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()

    @classmethod
    def from_yaml(cls, path: Path | None = None) -> "Settings":
        path = path or DEFAULT_CONFIG_PATH
        data = load_yaml_config(path)
        return cls(**data)


settings = Settings.from_yaml()
