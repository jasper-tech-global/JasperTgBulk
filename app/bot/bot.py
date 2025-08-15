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
from app.services.email_sender import send_email_smtp, EmailSendError
from app.utils.parsing import parse_command_text


async def handle_start(message: Message) -> None:
    await message.answer("Jasper TG BULK ready. Use /<template_code> <email> key=value ...")


async def handle_any_command(message: Message) -> None:
    chat_id = message.chat.id
    async with session_factory() as session:  # type: AsyncSession
        allowed = await session.execute(select(CustomerAllowlist).where(CustomerAllowlist.chat_id == chat_id))
        if not allowed.scalars().first():
            await message.answer("You are not a customer. Contact admin.")
            return
        try:
            code, recipient, variables = parse_command_text(message.text or "")
        except ValueError as exc:
            await message.answer("Invalid command format. Use /code email key=value")
            return
        tmpl_row = await session.execute(select(Template).where(Template.code == code, Template.active == True))
        template = tmpl_row.scalars().first()
        if not template:
            await message.answer("Unknown or inactive template code.")
            return
        smtp_row = await session.get(SmtpProfile, template.smtp_profile_id)
        if not smtp_row:
            await message.answer("SMTP profile not found.")
            return
        box = SecretBox(settings.fernet_key)
        password = box.decrypt(smtp_row.encrypted_password)
        subject = render_template_string(template.subject_template, variables)
        body = render_template_string(template.body_template, variables)
        try:
            await send_email_smtp(
                host=smtp_row.host,
                port=smtp_row.port,
                username=smtp_row.username,
                password=password,
                use_tls=smtp_row.use_tls,
                use_starttls=smtp_row.use_starttls,
                from_name=smtp_row.from_name,
                from_email=smtp_row.from_email,
                to_email=recipient,
                subject=subject,
                html_body=body,
            )
            await message.answer("Sent.")
        except EmailSendError as exc:
            await message.answer("Send failed.")


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_any_command, F.text.startswith("/"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
