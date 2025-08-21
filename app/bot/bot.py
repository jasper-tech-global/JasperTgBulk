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
        "💡 **Examples:**\n"
        "/welcome_email user@domain.com name=John\n"
        "/newsletter user1@domain.com,user2@domain.com month=December\n"
        "/promo\nuser1@domain.com\nuser2@domain.com\ndiscount=20%"
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
        
        # Get template
        tmpl_row = await session.execute(select(Template).where(Template.code == code, Template.active == True))
        template = tmpl_row.scalars().first()
        if not template:
            await message.answer("Unknown or inactive template code.")
            return
        
        # Determine if single or bulk
        is_bulk = len(recipients) > 1
        
        if is_bulk:
            # Bulk sending
            await message.answer(f"Sending to {len(recipients)} recipients...")
            
            try:
                subject = render_template_string(template.subject_template, variables)
                body = render_template_string(template.body_template, variables)
                
                # Use bulk sending service
                from app.services.email_sender import send_bulk_emails_with_random_smtp
                
                result = await send_bulk_emails_with_random_smtp(
                    session=session,
                    recipients=recipients,
                    subject_template=subject,
                    body_template=body,
                    timeout=30.0
                )
                
                success_msg = f"✅ Bulk email sent!\n📧 Total: {result['total_recipients']}\n✅ Successful: {result['successful_sends']}\n❌ Failed: {result['failed_sends']}"
                
                if result['smtp_usage']:
                    smtp_info = "\n📤 SMTP Usage:"
                    for smtp_name, count in result['smtp_usage'].items():
                        smtp_info += f"\n  • {smtp_name}: {count} emails"
                    success_msg += smtp_info
                
                await message.answer(success_msg)
                
            except Exception as exc:
                await message.answer(f"❌ Bulk send failed: {str(exc)}")
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


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_any_command, F.text.startswith("/"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
