from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from .config import settings
import os


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, future=True)
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db() -> None:
    os.makedirs("data", exist_ok=True)
    from app.models import customer, smtp_profile, template  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        await session.execute(text("PRAGMA journal_mode=WAL"))
        await session.commit()


async def get_session() -> AsyncSession:
    async with session_factory() as session:
        yield session
