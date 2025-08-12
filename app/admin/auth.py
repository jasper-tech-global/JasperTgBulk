from __future__ import annotations
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response
from starlette import status
from app.core.config import settings
from app.core.security import PasswordHasher, CookieSigner
from .deps import get_templates, optional_admin


router = APIRouter()
_hasher = PasswordHasher()
_signer = CookieSigner(settings.secret_key)


@router.get("/login")
async def login_page(request: Request, templates=Depends(get_templates), admin=Depends(optional_admin)):
    if admin:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == settings.admin_username and _hasher.verify(password, _hasher.hash(settings.admin_password)):
        token = _signer.dumps({"admin": True, "username": username})
        response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        response.set_cookie("session", token, httponly=True, samesite="lax")
        return response
    return RedirectResponse("/login?error=1", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout() -> Response:
    response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session")
    return response
