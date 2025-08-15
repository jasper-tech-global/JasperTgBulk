from __future__ import annotations
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_session
from app.core.config import settings
from app.core.security import SecretBox
from app.models import CustomerAllowlist, SmtpProfile, Template
from app.services.email_sender import send_email_smtp, EmailSendError
from .deps import get_templates, require_admin
import json


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


@router.post("/smtp/{row_id}/edit")
async def smtp_edit(
    row_id: int,
    name: str = Form(...),
    host: str = Form(...),
    port: int = Form(587),
    username: str = Form(...),
    password: str = Form(""),
    use_tls: bool = Form(False),
    use_starttls: bool = Form(True),
    from_name: str = Form(""),
    from_email: str = Form(...),
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    smtp_profile = await session.get(SmtpProfile, row_id)
    if not smtp_profile:
        raise HTTPException(status_code=404, detail="SMTP profile not found")
    
    # Update fields
    smtp_profile.name = name
    smtp_profile.host = host
    smtp_profile.port = port
    smtp_profile.username = username
    smtp_profile.use_tls = use_tls
    smtp_profile.use_starttls = use_starttls
    smtp_profile.from_name = from_name
    smtp_profile.from_email = from_email
    
    # Only update password if a new one is provided
    if password:
        box = SecretBox(settings.fernet_key)
        enc = box.encrypt(password)
        smtp_profile.encrypted_password = enc
    
    await session.commit()
    return RedirectResponse("/smtp", status_code=status.HTTP_302_FOUND)


@router.post("/smtp/{row_id}/delete")
async def smtp_delete(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    await session.execute(delete(SmtpProfile).where(SmtpProfile.id == row_id))
    await session.commit()
    return RedirectResponse("/smtp", status_code=status.HTTP_302_FOUND)


@router.post("/api/smtp/test")
async def smtp_test(request: Request, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    try:
        body = await request.json()
        profile_id = body.get("profile_id")
        test_email = body.get("test_email")
        
        if not profile_id or not test_email:
            raise HTTPException(status_code=400, detail="Missing profile_id or test_email")
        
        smtp_profile = await session.get(SmtpProfile, profile_id)
        if not smtp_profile:
            raise HTTPException(status_code=404, detail="SMTP profile not found")
        
        box = SecretBox(settings.fernet_key)
        password = box.decrypt(smtp_profile.encrypted_password)
        
        await send_email_smtp(
            host=smtp_profile.host,
            port=smtp_profile.port,
            username=smtp_profile.username,
            password=password,
            use_tls=smtp_profile.use_tls,
            use_starttls=smtp_profile.use_starttls,
            from_name=smtp_profile.from_name or "Test Email",
            from_email=smtp_profile.from_email,
            to_email=test_email,
            subject="SMTP Test - Jasper TG BULK",
            html_body="""
            <html>
            <body>
                <h2>SMTP Test Successful! 🎉</h2>
                <p>This is a test email from your Jasper TG BULK bot configuration.</p>
                <p><strong>SMTP Profile:</strong> {profile_name}</p>
                <p><strong>Server:</strong> {host}:{port}</p>
                <p><strong>From:</strong> {from_name} &lt;{from_email}&gt;</p>
                <p><strong>Security:</strong> {security}</p>
                <hr>
                <p><em>If you received this email, your SMTP configuration is working correctly!</em></p>
            </body>
            </html>
            """.format(
                profile_name=smtp_profile.name,
                host=smtp_profile.host,
                port=smtp_profile.port,
                from_name=smtp_profile.from_name or "Test",
                from_email=smtp_profile.from_email,
                security="TLS" if smtp_profile.use_tls else "STARTTLS" if smtp_profile.use_starttls else "None"
            )
        )
        
        return JSONResponse({"success": True, "message": "Test email sent successfully"})
        
    except EmailSendError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Unexpected error: {str(e)}"}, status_code=500)


@router.post("/api/bot/test")
async def bot_test(request: Request, admin=Depends(require_admin)):
    try:
        from aiogram import Bot
        
        if not settings.telegram_bot_token:
            return JSONResponse({"success": False, "error": "Bot token not configured"}, status_code=400)
        
        bot = Bot(token=settings.telegram_bot_token)
        me = await bot.get_me()
        await bot.session.close()
        
        return JSONResponse({
            "success": True, 
            "message": "Bot connection successful",
            "bot_info": {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name
            }
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


@router.get("/templates")
async def templates_page(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    try:
        stmt = select(Template).options(selectinload(Template.smtp_profile)).order_by(Template.id.desc())
        rows = (await session.execute(stmt)).scalars().all()
        smtp_rows = (await session.execute(select(SmtpProfile).order_by(SmtpProfile.name.asc()))).scalars().all()
        return templates.TemplateResponse("templates.html", {"request": request, "rows": rows, "smtp_rows": smtp_rows})
    except Exception as e:
        # Log the error for debugging
        print(f"Error in templates route: {e}")
        # Return empty data to prevent crash
        return templates.TemplateResponse("templates.html", {"request": request, "rows": [], "smtp_rows": []})


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
