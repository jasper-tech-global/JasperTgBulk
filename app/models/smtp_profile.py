from __future__ import annotations
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SmtpProfile(Base):
    __tablename__ = "smtp_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=587)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(String(255), nullable=False)
    use_tls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    use_starttls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    from_name: Mapped[str] = mapped_column(String(255), nullable=True)
    from_email: Mapped[str] = mapped_column(String(320), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
