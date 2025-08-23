from __future__ import annotations
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import session_factory
from app.core.security import SecretBox
from app.models import CustomerAllowlist, Template, SmtpProfile
from app.services.template_renderer import render_template_string
from app.services.email_sender import send_email_smtp, send_email_with_random_smtp, EmailSendError
from app.utils.parsing import parse_command_text


async def handle_start(message: Message) -> None:
    await message.answer(
        "🚀 Jasper TG BULK ready!\n\n"
        "📧 **Single Email:**\n"
        "/<template_code> email@domain.com key=value\n\n"
        "📧 **Bulk Emails (comma):**\n"
        "/<template_code> email1@domain.com,email2@domain.com key=value\n\n"
        "📧 **Bulk Emails (newline):**\n"
        "/<template_code>\nemail1@domain.com\nemail2@domain.com\nkey=value\n\n"
        "🎲 **Random Templates (Anti-Spam):**\n"
        "/random template1,template2,template3 email1@domain.com,email2@domain.com key=value\n\n"
        "💡 **Examples:**\n"
        "/welcome_email user@domain.com name=John\n"
        "/newsletter user1@domain.com,user2@domain.com month=December\n"
        "/promo\nuser1@domain.com\nuser2@domain.com\ndiscount=20%\n"
        "/random welcome,promo,newsletter user1@domain.com,user2@domain.com,user3@domain.com name=John"
    )


async def handle_any_command(message: Message) -> None:
    chat_id = message.chat.id
    async with session_factory() as session:  # type: AsyncSession
        # Check if user is allowed
        allowed = await session.execute(select(CustomerAllowlist).where(CustomerAllowlist.chat_id == chat_id))
        if not allowed.scalars().first():
            await message.answer("You are not a customer. Contact admin.")
            return
        
        try:
            code, recipients, variables = parse_command_text(message.text or "")
        except ValueError as exc:
            await message.answer("Invalid command format. Use /code email key=value or /code email1,email2 key=value")
            return
        
        # Check if this is a random template command
        if code == "random":
            await handle_random_template_command(message, session, recipients, variables)
            return
        
        # Get template
        tmpl_row = await session.execute(select(Template).where(Template.code == code, Template.active == True))
        template = tmpl_row.scalars().first()
        if not template:
            await message.answer("Unknown or inactive template code.")
            return
        
        # Determine if single or bulk
        is_bulk = len(recipients) > 1
        
        if is_bulk:
            # Enhanced bulk sending with breaktime and progress tracking
            await handle_enhanced_bulk_sending(message, session, template, recipients, variables)
        else:
            # Single email sending
            try:
                subject = render_template_string(template.subject_template, variables)
                body = render_template_string(template.body_template, variables)
                
                result = await send_email_with_random_smtp(
                    session=session,
                    to_email=recipients[0],
                    subject=subject,
                    html_body=body,
                    timeout=30.0
                )
                
                await message.answer(f"✅ Email sent to {recipients[0]} using {result['smtp_profile']['name']}")
                
            except EmailSendError as exc:
                await message.answer(f"❌ Send failed: {str(exc)}")
            except Exception as exc:
                await message.answer(f"❌ Unexpected error: {str(exc)}")


async def handle_random_template_command(message: Message, session: AsyncSession, recipients: list, variables: dict) -> None:
    """Handle the /random command for anti-spam template randomization"""
    
    # Extract template codes from variables (first recipient is actually template codes)
    if not recipients:
        await message.answer("❌ Invalid format. Use: /random template1,template2,template3 email1@domain.com,email2@domain.com key=value")
        return
    
    # First recipient contains template codes
    template_codes_text = recipients[0]
    if ',' not in template_codes_text:
        await message.answer("❌ Invalid format. Use: /random template1,template2,template3 email1@domain.com,email2@domain.com key=value")
        return
    
    # Parse template codes and actual recipients
    template_codes = [code.strip() for code in template_codes_text.split(',') if code.strip()]
    actual_recipients = recipients[1:] if len(recipients) > 1 else []
    
    if not template_codes or not actual_recipients:
        await message.answer("❌ Invalid format. Use: /random template1,template2,template3 email1@domain.com,email2@domain.com key=value")
        return
    
    # Validate templates exist
    stmt = select(Template).where(Template.code.in_(template_codes), Template.active == True)
    result = await session.execute(stmt)
    available_templates = result.scalars().all()
    
    if len(available_templates) != len(template_codes):
        found_codes = [tmpl.code for tmpl in available_templates]
        missing_codes = [code for code in template_codes if code not in found_codes]
        await message.answer(f"❌ Some templates not found or inactive: {', '.join(missing_codes)}")
        return
    
    # Start random template campaign
    await message.answer(f"🎲 Starting random template campaign!\n📧 Templates: {', '.join(template_codes)}\n📬 Recipients: {len(actual_recipients)}")
    
    try:
        # Progress tracking callback for real-time updates
        async def progress_callback(progress_data):
            status = progress_data.get("status")
            message_text = progress_data.get("message", "")
            
            if status == "starting":
                await message.answer(f"🚀 {message_text}")
            elif status == "sending":
                await message.answer(f"📧 {message_text}")
            elif status == "sent":
                await message.answer(f"✅ {message_text}")
            elif status == "failed":
                await message.answer(f"❌ {message_text}")
            elif status == "waiting":
                await message.answer(f"⏳ {message_text}")
            elif status == "completed":
                # Build completion message
                completion_message = f"🎉 {message_text}\n\n"
                
                # Add timing summary for 10+ emails
                if progress_data.get("total", 0) >= 10:
                    timing = progress_data.get("timing_summary", {})
                    completion_message += f"⏱️ **Timing Summary:**\n"
                    completion_message += f"   • Total Duration: {timing.get('total_duration', 'N/A')}\n"
                    completion_message += f"   • Average per Email: {timing.get('average_time_per_email', 'N/A')}\n"
                    completion_message += f"   • Total Breaktime: {timing.get('total_breaktime', 'N/A')}\n"
                    completion_message += f"   • Breaktime Range: {timing.get('breaktime_range', 'N/A')}\n\n"
                
                # Add template usage summary
                template_summary = progress_data.get("template_summary", {})
                if template_summary:
                    completion_message += f"📋 **Template Usage:**\n"
                    for template_code, count in template_summary.items():
                        completion_message += f"   • {template_code}: {count} emails\n"
                    completion_message += "\n"
                
                # Add SMTP usage summary
                smtp_summary = progress_data.get("smtp_summary", {})
                if smtp_summary:
                    completion_message += f"📤 **SMTP Usage:**\n"
                    for smtp_name, count in smtp_summary.items():
                        completion_message += f"   • {smtp_name}: {count} emails\n"
                
                await message.answer(completion_message)
        
        # Send bulk emails with random templates
        from app.services.email_sender import send_bulk_emails_with_random_templates
        
        result = await send_bulk_emails_with_random_templates(
            session=session,
            recipients=actual_recipients,
            template_codes=template_codes,
            variables=variables,
            min_breaktime=6.0,
            max_breaktime=15.0,
            timeout=30.0,
            progress_callback=progress_callback,
            use_content_variation=True
        )
        
        # Final confirmation
        if result["successful_sends"] > 0:
            await message.answer(f"🎯 Campaign completed successfully! {result['successful_sends']} emails sent with anti-spam optimization.")
        else:
            await message.answer(f"❌ Campaign failed. No emails were sent successfully.")
            
    except Exception as exc:
        await message.answer(f"❌ Random template campaign failed: {str(exc)}")


async def handle_enhanced_bulk_sending(message: Message, session: AsyncSession, template, recipients: list, variables: dict) -> None:
    """Handle enhanced bulk sending with breaktime and progress tracking"""
    
    await message.answer(f"🚀 Starting enhanced bulk email campaign to {len(recipients)} recipients\n⏱️ Breaktime: 6-15 seconds between emails")
    
    try:
        subject = render_template_string(template.subject_template, variables)
        body = render_template_string(template.body_template, variables)
        
        # Progress tracking callback for real-time updates
        async def progress_callback(progress_data):
            status = progress_data.get("status")
            message_text = progress_data.get("message", "")
            
            if status == "starting":
                await message.answer(f"🚀 {message_text}")
            elif status == "sending":
                await message.answer(f"📧 {message_text}")
            elif status == "sent":
                await message.answer(f"✅ {message_text}")
            elif status == "failed":
                await message.answer(f"❌ {message_text}")
            elif status == "waiting":
                await message.answer(f"⏳ {message_text}")
            elif status == "completed":
                # Build completion message
                completion_message = f"🎉 {message_text}\n\n"
                
                # Add timing summary for 10+ emails
                if progress_data.get("total", 0) >= 10:
                    timing = progress_data.get("timing_summary", {})
                    completion_message += f"⏱️ **Timing Summary:**\n"
                    completion_message += f"   • Total Duration: {timing.get('total_duration', 'N/A')}\n"
                    completion_message += f"   • Average per Email: {timing.get('average_time_per_email', 'N/A')}\n"
                    completion_message += f"   • Total Breaktime: {timing.get('total_breaktime', 'N/A')}\n"
                    completion_message += f"   • Breaktime Range: {timing.get('breaktime_range', 'N/A')}\n\n"
                
                # Add SMTP usage summary
                smtp_summary = progress_data.get("smtp_usage", {})
                if smtp_summary:
                    completion_message += f"📤 **SMTP Usage:**\n"
                    for smtp_name, count in smtp_summary.items():
                        completion_message += f"   • {smtp_name}: {count} emails\n"
                
                await message.answer(completion_message)
        
        # Send bulk emails with breaktime
        from app.services.email_sender import send_bulk_emails_with_breaktime
        
        result = await send_bulk_emails_with_breaktime(
            session=session,
            recipients=recipients,
            subject_template=subject,
            body_template=body,
            min_breaktime=6.0,
            max_breaktime=15.0,
            timeout=30.0,
            progress_callback=progress_callback,
            use_content_variation=True
        )
        
        # Final confirmation
        if result["successful_sends"] > 0:
            await message.answer(f"🎯 Campaign completed successfully! {result['successful_sends']} emails sent with anti-spam optimization.")
        else:
            await message.answer(f"❌ Campaign failed. No emails were sent successfully.")
        
    except Exception as exc:
        await message.answer(f"❌ Enhanced bulk send failed: {str(exc)}")


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_any_command, F.text.startswith("/"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
