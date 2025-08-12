from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr


class SmtpProfileBase(BaseModel):
    name: str
    host: str
    port: int = Field(default=587)
    username: str
    password: str
    use_tls: bool = Field(default=False)
    use_starttls: bool = Field(default=True)
    from_name: str = Field(default="")
    from_email: EmailStr


class SmtpProfileCreate(SmtpProfileBase):
    pass


class SmtpProfileOut(BaseModel):
    id: int
    name: str
    host: str
    port: int
    username: str
    use_tls: bool
    use_starttls: bool
    from_name: str
    from_email: EmailStr

    class Config:
        from_attributes = True
