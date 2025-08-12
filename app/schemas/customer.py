from __future__ import annotations
from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    chat_id: int = Field(..., ge=1)
    label: str = Field(default="")


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int

    class Config:
        from_attributes = True
