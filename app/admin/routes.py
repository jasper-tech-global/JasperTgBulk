from __future__ import annotations
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_session
from app.core.config import settings
from app.core.security import SecretBox
from app.models import CustomerAllowlist, SmtpProfile, Template
from .deps import get_templates, require_admin


router = APIRouter()


@router.get("/")
async def dashboard(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    total_customers = (await session.execute(select(CustomerAllowlist))).scalars().all()
    total_templates = (await session.execute(select(Template))).scalars().all()
    total_smtp = (await session.execute(select(SmtpProfile))).scalars().all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "customers": len(total_customers), "templates": len(total_templates), "smtps": len(total_smtp)})


@router.get("/customers")
async def customers_page(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(CustomerAllowlist).order_by(CustomerAllowlist.created_at.desc()))).scalars().all()
    return templates.TemplateResponse("customers.html", {"request": request, "rows": rows})


@router.post("/customers")
async def customers_create(chat_id: int = Form(...), label: str = Form(""), session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    row = CustomerAllowlist(chat_id=chat_id, label=label)
    session.add(row)
    await session.commit()
    return RedirectResponse("/customers", status_code=status.HTTP_302_FOUND)


@router.post("/customers/{row_id}/delete")
async def customers_delete(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    await session.execute(delete(CustomerAllowlist).where(CustomerAllowlist.id == row_id))
    await session.commit()
    return RedirectResponse("/customers", status_code=status.HTTP_302_FOUND)


@router.get("/smtp")
async def smtp_page(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(SmtpProfile).order_by(SmtpProfile.created_at.desc()))).scalars().all()
    return templates.TemplateResponse("smtp_profiles.html", {"request": request, "rows": rows})


@router.post("/smtp")
async def smtp_create(
    name: str = Form(...),
    host: str = Form(...),
    port: int = Form(587),
    username: str = Form(...),
    password: str = Form(...),
    use_tls: bool = Form(False),
    use_starttls: bool = Form(True),
    from_name: str = Form(""),
    from_email: str = Form(...),
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    box = SecretBox(settings.fernet_key)
    enc = box.encrypt(password)
    row = SmtpProfile(
        name=name,
        host=host,
        port=port,
        username=username,
        encrypted_password=enc,
        use_tls=use_tls,
        use_starttls=use_starttls,
        from_name=from_name,
        from_email=from_email,
    )
    session.add(row)
    await session.commit()
    return RedirectResponse("/smtp", status_code=status.HTTP_302_FOUND)


@router.post("/smtp/{row_id}/delete")
async def smtp_delete(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    await session.execute(delete(SmtpProfile).where(SmtpProfile.id == row_id))
    await session.commit()
    return RedirectResponse("/smtp", status_code=status.HTTP_302_FOUND)


@router.get("/templates")
async def templates_page(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    stmt = select(Template).options(selectinload(Template.smtp_profile)).order_by(Template.created_at.desc())
    rows = (await session.execute(stmt)).scalars().all()
    smtp_rows = (await session.execute(select(SmtpProfile).order_by(SmtpProfile.name.asc()))).scalars().all()
    return templates.TemplateResponse("templates.html", {"request": request, "rows": rows, "smtp_rows": smtp_rows})


@router.post("/templates")
async def templates_create(
    code: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    smtp_profile_id: int = Form(...),
    active: bool = Form(False),
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    row = Template(code=code, subject_template=subject_template, body_template=body_template, smtp_profile_id=smtp_profile_id, active=active)
    session.add(row)
    await session.commit()
    return RedirectResponse("/templates", status_code=status.HTTP_302_FOUND)


@router.post("/templates/{row_id}/delete")
async def templates_delete(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    await session.execute(delete(Template).where(Template.id == row_id))
    await session.commit()
    return RedirectResponse("/templates", status_code=status.HTTP_302_FOUND)
