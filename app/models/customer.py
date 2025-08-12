from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Integer, DateTime, func, UniqueConstraint
from app.core.database import Base


class CustomerAllowlist(Base):
    __tablename__ = "customer_allowlist"
    __table_args__ = (UniqueConstraint("chat_id", name="uq_customer_chat_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
