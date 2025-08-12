from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, func
from app.core.database import Base


class SmtpProfile(Base):
    __tablename__ = "smtp_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=587)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(String(2048), nullable=False)
    use_tls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    use_starttls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    from_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    from_email: Mapped[str] = mapped_column(String(320), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    templates = relationship("Template", back_populates="smtp_profile")
