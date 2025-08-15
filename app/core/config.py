from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    secret_key: str = os.getenv("SECRET_KEY", "")
    fernet_key: str = os.getenv("FERNET_KEY", "")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))


settings = Settings()
