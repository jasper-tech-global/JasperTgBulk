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
    await message.answer("Jasper TG BULK ready. Use /<template_code> <email> key=value ...")


async def handle_any_command(message: Message) -> None:
    chat_id = message.chat.id
    async with session_factory() as session:  # type: AsyncSession
        # Check if user is allowed
        allowed = await session.execute(select(CustomerAllowlist).where(CustomerAllowlist.chat_id == chat_id))
        if not allowed.scalars().first():
            await message.answer("You are not a customer. Contact admin.")
            return
        
        try:
            code, recipient, variables = parse_command_text(message.text or "")
        except ValueError as exc:
            await message.answer("Invalid command format. Use /code email key=value")
            return
        
        # Get template
        tmpl_row = await session.execute(select(Template).where(Template.code == code, Template.active == True))
        template = tmpl_row.scalars().first()
        if not template:
            await message.answer("Unknown or inactive template code.")
            return
        
        # Send email using random SMTP profile selection
        try:
            subject = render_template_string(template.subject_template, variables)
            body = render_template_string(template.body_template, variables)
            
            result = await send_email_with_random_smtp(
                session=session,
                to_email=recipient,
                subject=subject,
                html_body=body,
                timeout=30.0
            )
            
            await message.answer("Sent.")
            
        except EmailSendError as exc:
            await message.answer(f"Send failed: {str(exc)}")
        except Exception as exc:
            await message.answer(f"Unexpected error: {str(exc)}")


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_any_command, F.text.startswith("/"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
