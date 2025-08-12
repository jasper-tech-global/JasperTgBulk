from __future__ import annotations
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from app.core.security import CookieSigner
from app.core.config import settings


templates = Jinja2Templates(directory="templates")
_signer = CookieSigner(settings.secret_key)


def get_templates() -> Jinja2Templates:
    return templates


def require_admin(request: Request) -> dict:
    session = request.cookies.get("session")
    data = _signer.loads(session) if session else None
    if not data or not data.get("admin"):
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": "/login"})
    return data


def optional_admin(request: Request) -> dict | None:
    session = request.cookies.get("session")
    return _signer.loads(session) if session else None
