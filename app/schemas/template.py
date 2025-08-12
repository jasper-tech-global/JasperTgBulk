from __future__ import annotations
from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    subject_template: str
    body_template: str
    smtp_profile_id: int
    active: bool = Field(default=True)


class TemplateCreate(TemplateBase):
    pass


class TemplateOut(TemplateBase):
    id: int

    class Config:
        from_attributes = True
