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
    try:
        # Get total customers
        stmt = select(CustomerAllowlist)
        result = await session.execute(stmt)
        total_customers = len(result.scalars().all())
        
        # Get total SMTP profiles
        stmt = select(SmtpProfile)
        result = await session.execute(stmt)
        total_smtp_profiles = len(result.scalars().all())
        
        # Get total templates
        stmt = select(Template)
        result = await session.execute(stmt)
        total_templates = len(result.scalars().all())
        
        # Get active SMTP profiles
        stmt = select(SmtpProfile).where(SmtpProfile.active == True)
        result = await session.execute(stmt)
        active_smtp_profiles = len(result.scalars().all())
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_customers": total_customers,
            "total_smtp_profiles": total_smtp_profiles,
            "total_templates": total_templates,
            "active_smtp_profiles": active_smtp_profiles
        })
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        # Return dashboard with default values if there's an error
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_customers": 0,
            "total_smtp_profiles": 0,
            "total_templates": 0,
            "active_smtp_profiles": 0
        })


@router.get("/customers")
async def customers_page(request: Request, templates=Depends(get_templates), admin=Depends(require_admin), session: AsyncSession = Depends(get_session)):
    try:
        stmt = select(CustomerAllowlist).order_by(CustomerAllowlist.created_at.desc())
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return templates.TemplateResponse("customers.html", {"request": request, "rows": rows})
    except Exception as e:
        print(f"Error in customers route: {e}")
        # Return page with empty rows if there's an error
        return templates.TemplateResponse("customers.html", {"request": request, "rows": []})


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
    try:
        stmt = select(SmtpProfile).order_by(SmtpProfile.created_at.desc())
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return templates.TemplateResponse("smtp_profiles.html", {"request": request, "rows": rows})
    except Exception as e:
        print(f"Error in SMTP profiles route: {e}")
        # Return page with empty rows if there's an error
        return templates.TemplateResponse("smtp_profiles.html", {"request": request, "rows": []})


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
    active: bool = Form(True),
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
        active=active,
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


@router.post("/api/smtp/{row_id}/toggle-active")
async def smtp_toggle_active(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    """Toggle the active status of an SMTP profile"""
    try:
        smtp_profile = await session.get(SmtpProfile, row_id)
        if not smtp_profile:
            raise HTTPException(status_code=404, detail="SMTP profile not found")
        
        # Toggle active status
        smtp_profile.active = not smtp_profile.active
        await session.commit()
        
        status_text = "activated" if smtp_profile.active else "deactivated"
        return JSONResponse({
            "success": True, 
            "message": f"SMTP profile '{smtp_profile.name}' {status_text}",
            "active": smtp_profile.active
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Error toggling status: {str(e)}"}, status_code=500)


@router.post("/api/smtp/{row_id}/delete")
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
        
        # Use the enhanced test email function with inbox delivery optimization
        from app.services.email_sender import send_test_email_with_delivery_verification
        
        result = await send_test_email_with_delivery_verification(
            host=smtp_profile.host,
            port=smtp_profile.port,
            username=smtp_profile.username,
            password=password,
            use_tls=smtp_profile.use_tls,
            use_starttls=smtp_profile.use_starttls,
            from_name=smtp_profile.from_name or "Test Email",
            from_email=smtp_profile.from_email,
            to_email=test_email,
            timeout=30.0
        )
        
        if result["sending_success"]:
            return JSONResponse({
                "success": True, 
                "message": "Test email sent successfully with inbox delivery optimization!",
                "message_id": result["message_id"],
                "delivery_optimization": result["delivery_optimization"],
                "recommendations": result["recommendations"]
            })
        else:
            return JSONResponse({
                "success": False, 
                "error": "Failed to send test email",
                "details": result.get("errors", []),
                "recommendations": result.get("recommendations", [])
            }, status_code=400)
        
    except EmailSendError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Unexpected error: {str(e)}"}, status_code=500)


@router.post("/api/smtp/diagnostics")
async def smtp_diagnostics(request: Request, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    """Comprehensive SMTP diagnostics for inbox delivery optimization"""
    try:
        body = await request.json()
        profile_id = body.get("profile_id")
        
        if not profile_id:
            raise HTTPException(status_code=400, detail="Missing profile_id")
        
        smtp_profile = await session.get(SmtpProfile, profile_id)
        if not smtp_profile:
            raise HTTPException(status_code=404, detail="SMTP profile not found")
        
        box = SecretBox(settings.fernet_key)
        password = box.decrypt(smtp_profile.encrypted_password)
        
        # Use the enhanced diagnostics function
        from app.services.email_sender import test_smtp_connection
        
        diagnostics = await test_smtp_connection(
            host=smtp_profile.host,
            port=smtp_profile.port,
            username=smtp_profile.username,
            password=password,
            use_tls=smtp_profile.use_tls,
            use_starttls=smtp_profile.use_starttls,
            timeout=15.0
        )
        
        # Add profile-specific recommendations
        diagnostics["profile_info"] = {
            "name": smtp_profile.name,
            "host": smtp_profile.host,
            "port": smtp_profile.port,
            "use_tls": smtp_profile.use_tls,
            "use_starttls": smtp_profile.use_starttls,
            "from_email": smtp_profile.from_email
        }
        
        # Add inbox delivery score
        delivery_score = 0
        if diagnostics["connection_success"]:
            delivery_score += 25
        if diagnostics["authentication_success"]:
            delivery_score += 25
        if smtp_profile.use_tls or smtp_profile.use_starttls:
            delivery_score += 25
        if smtp_profile.port in [587, 465]:
            delivery_score += 25
        
        diagnostics["inbox_delivery_score"] = delivery_score
        diagnostics["inbox_delivery_rating"] = "Excellent" if delivery_score >= 90 else "Good" if delivery_score >= 75 else "Fair" if delivery_score >= 50 else "Poor"
        
        return JSONResponse(diagnostics)
        
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Diagnostics error: {str(e)}"}, status_code=500)


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
        stmt = select(Template).order_by(Template.id.desc())
        rows = (await session.execute(stmt)).scalars().all()
        return templates.TemplateResponse("templates.html", {"request": request, "rows": rows})
    except Exception as e:
        print(f"Error in templates route: {e}")
        return templates.TemplateResponse("templates.html", {"request": request, "rows": []})


@router.post("/templates")
async def templates_create(
    code: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    active: bool = Form(False),
    smtp_profile_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    try:
        # Verify SMTP profile exists and is active
        smtp_profile = await session.get(SmtpProfile, smtp_profile_id)
        if not smtp_profile:
            raise HTTPException(status_code=400, detail="Selected SMTP profile not found")
        
        if not smtp_profile.active:
            raise HTTPException(status_code=400, detail="Selected SMTP profile is not active")
        
        row = Template(
            code=code, 
            subject_template=subject_template, 
            body_template=body_template, 
            active=active,
            smtp_profile_id=smtp_profile_id
        )
        session.add(row)
        await session.commit()
        
        return RedirectResponse("/templates", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.post("/templates/{template_id}/edit")
async def templates_edit(
    template_id: int,
    code: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    active: bool = Form(False),
    smtp_profile_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    """Edit an existing template"""
    try:
        # Get the template to edit
        template = await session.get(Template, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Verify SMTP profile exists and is active
        smtp_profile = await session.get(SmtpProfile, smtp_profile_id)
        if not smtp_profile:
            raise HTTPException(status_code=400, detail="Selected SMTP profile not found")
        
        if not smtp_profile.active:
            raise HTTPException(status_code=400, detail="Selected SMTP profile is not active")
        
        # Update template fields
        template.code = code
        template.subject_template = subject_template
        template.body_template = body_template
        template.active = active
        template.smtp_profile_id = smtp_profile_id
        
        await session.commit()
        
        return RedirectResponse("/templates", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to edit template: {str(e)}")


@router.get("/api/templates/{template_id}")
async def get_template_api(
    template_id: int,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    """Get template data for editing"""
    try:
        template = await session.get(Template, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get SMTP profile info
        smtp_profile = await session.get(SmtpProfile, template.smtp_profile_id) if template.smtp_profile_id else None
        
        return JSONResponse({
            "success": True,
            "template": {
                "id": template.id,
                "code": template.code,
                "subject_template": template.subject_template,
                "body_template": template.body_template,
                "active": template.active,
                "smtp_profile_id": template.smtp_profile_id,
                "smtp_profile_name": smtp_profile.name if smtp_profile else None
            }
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/api/send-email")
async def send_email_api(request: Request, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    """Send email using random SMTP profile selection"""
    try:
        body = await request.json()
        template_code = body.get("template_code")
        recipient_email = body.get("recipient_email")
        variables = body.get("variables", {})
        
        if not template_code or not recipient_email:
            raise HTTPException(status_code=400, detail="Missing template_code or recipient_email")
        
        # Get template
        template = await session.get(Template, template_code)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if not template.active:
            raise HTTPException(status_code=400, detail="Template is not active")
        
        # Render template with variables
        from jinja2 import Template as JinjaTemplate
        
        try:
            subject = JinjaTemplate(template.subject_template).render(**variables)
            body_html = JinjaTemplate(template.body_template).render(**variables)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
        
        # Send email with random SMTP
        from app.services.email_sender import send_email_with_random_smtp
        
        result = await send_email_with_random_smtp(
            session=session,
            to_email=recipient_email,
            subject=subject,
            html_body=body_html,
            timeout=30.0
        )
        
        return JSONResponse({
            "success": True,
            "message": "Email sent successfully with random SMTP selection",
            "smtp_profile": result["smtp_profile"],
            "delivery_optimization": result["delivery_optimization"]
        })
        
    except EmailSendError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Unexpected error: {str(e)}"}, status_code=500)


@router.post("/api/send-bulk-emails")
async def send_bulk_emails_api(request: Request, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    """Send bulk emails using random SMTP profile selection"""
    try:
        body = await request.json()
        template_code = body.get("template_code")
        recipient_emails = body.get("recipient_emails", [])
        variables = body.get("variables", {})
        
        if not template_code or not recipient_emails:
            raise HTTPException(status_code=400, detail="Missing template_code or recipient_emails")
        
        if not isinstance(recipient_emails, list) or len(recipient_emails) == 0:
            raise HTTPException(status_code=400, detail="recipient_emails must be a non-empty list")
        
        # Get template
        template = await session.get(Template, template_code)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if not template.active:
            raise HTTPException(status_code=400, detail="Template is not active")
        
        # Render template with variables
        from jinja2 import Template as JinjaTemplate
        
        try:
            subject = JinjaTemplate(template.subject_template).render(**variables)
            body_html = JinjaTemplate(template.body_template).render(**variables)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
        
        # Send bulk emails with random SMTP
        from app.services.email_sender import send_bulk_emails_with_random_smtp
        
        result = await send_bulk_emails_with_random_smtp(
            session=session,
            recipients=recipient_emails,
            subject_template=subject,
            body_template=body_html,
            timeout=30.0
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Bulk emails sent: {result['successful_sends']} successful, {result['failed_sends']} failed",
            "results": result
        })
        
    except EmailSendError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Unexpected error: {str(e)}"}, status_code=500)


@router.post("/templates/{row_id}/delete")
async def templates_delete(row_id: int, session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    await session.execute(delete(Template).where(Template.id == row_id))
    await session.commit()
    return RedirectResponse("/templates", status_code=status.HTTP_302_FOUND)


@router.get("/api/smtp")
async def get_smtp_profiles_api(session: AsyncSession = Depends(get_session), admin=Depends(require_admin)):
    """Get all SMTP profiles for dropdown selection"""
    try:
        stmt = select(SmtpProfile).order_by(SmtpProfile.name)
        result = await session.execute(stmt)
        profiles = result.scalars().all()
        
        return JSONResponse({
            "success": True,
            "profiles": [
                {
                    "id": profile.id,
                    "name": profile.name,
                    "host": profile.host,
                    "port": profile.port,
                    "from_email": profile.from_email,
                    "active": profile.active
                }
                for profile in profiles
            ]
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
