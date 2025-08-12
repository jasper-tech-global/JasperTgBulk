from __future__ import annotations
from email.message import EmailMessage
from aiosmtplib import SMTP, SMTPException
from typing import Optional


class EmailSendError(Exception):
    pass


async def send_email_smtp(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool,
    use_starttls: bool,
    from_name: str,
    from_email: str,
    to_email: str,
    subject: str,
    html_body: str,
    timeout: Optional[float] = 30.0,
) -> None:
    message = EmailMessage()
    message["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content("This message requires an HTML-compatible email client.")
    message.add_alternative(html_body, subtype="html")
    try:
        if use_tls:
            async with SMTP(hostname=host, port=port, use_tls=True, timeout=timeout) as smtp:
                await smtp.login(username, password)
                await smtp.send_message(message)
        else:
            async with SMTP(hostname=host, port=port, timeout=timeout) as smtp:
                if use_starttls:
                    await smtp.starttls()
                await smtp.login(username, password)
                await smtp.send_message(message)
    except SMTPException as exc:
        raise EmailSendError(str(exc)) from exc
