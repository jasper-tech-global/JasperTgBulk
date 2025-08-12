from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./data/app.db")
    telegram_bot_token: str = Field(default="")
    secret_key: str = Field(default="")
    fernet_key: str = Field(default="")
    admin_username: str = Field(default="admin")
    admin_password: str = Field(default="change-me")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
