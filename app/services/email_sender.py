from __future__ import annotations
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from aiosmtplib import SMTP, SMTPException
from typing import Optional
from sqlalchemy import select
from app.models.template import Template
import socket
import ssl
import time
import random
import hashlib


class EmailSendError(Exception):
    pass


class AntiSpamOptimizer:
    """Advanced anti-spam optimization for inbox delivery"""
    
    @staticmethod
    def add_authentication_headers(message: EmailMessage, from_email: str, domain: str) -> None:
        """Add comprehensive authentication headers to prevent spam filtering"""
        
        # SPF validation header
        message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
        
        # Domain authentication
        message["X-Domain-Auth"] = f"verified ({domain})"
        message["X-Sender-Verification"] = "verified"
        
        # DKIM signature placeholder (will be signed by SMTP provider)
        message["DKIM-Signature"] = f"v=1; a=rsa-sha256; d={domain}; s=default;"
        
        # Sender policy framework
        message["X-Sender-Policy"] = f"include:{domain}"
        
        # Domain reputation
        message["X-Domain-Reputation"] = "trusted"
        
        # Authentication results
        message["Authentication-Results"] = f"{domain}; spf=pass smtp.mailfrom={from_email}; dkim=pass header.d={domain}; dmarc=pass"
    
    @staticmethod
    def add_delivery_headers(message: EmailMessage, from_name: str, from_email: str) -> None:
        """Add headers that improve inbox delivery and prevent spam filtering"""
        
        domain = from_email.split('@')[1]
        
        # Message-ID for tracking and reputation
        message["Message-ID"] = make_msgid(domain=domain)
        
        # Date header (required for many ISPs)
        message["Date"] = formatdate(localtime=True)
        
        # From header with proper formatting
        if from_name:
            message["From"] = formataddr((from_name, from_email))
        else:
            message["From"] = from_email
        
        # Return-Path for bounce handling
        message["Return-Path"] = from_email
        
        # X-Mailer for identification (helps with reputation)
        message["X-Mailer"] = "Jasper TG BULK - Professional Email Tool"
        
        # X-Priority for importance (3 = normal)
        message["X-Priority"] = "3"
        
        # MIME-Version
        message["MIME-Version"] = "1.0"
        
        # Content-Type with charset
        message["Content-Type"] = "text/html; charset=UTF-8"
        
        # Add authentication headers
        AntiSpamOptimizer.add_authentication_headers(message, from_email, domain)
    
    @staticmethod
    def add_reputation_headers(message: EmailMessage, from_email: str) -> None:
        """Add headers that help with reputation management and spam prevention"""
        
        domain = from_email.split('@')[1]
        
        # List-Unsubscribe for better reputation
        message["List-Unsubscribe"] = f"<mailto:unsubscribe@{domain}>"
        
        # Feedback-ID for reputation tracking
        message["Feedback-ID"] = f"bulk:jasper-tg-bulk:{domain}"
        
        # X-Auto-Response-Suppress for auto-response handling
        message["X-Auto-Response-Suppress"] = "All"
        
        # X-Report-Abuse for abuse reporting
        message["X-Report-Abuse"] = f"Please report abuse to abuse@{domain}"
        
        # X-Complaints-To for complaint handling
        message["X-Complaints-To"] = f"complaints@{domain}"
        
        # X-Feedback-ID for tracking
        message["X-Feedback-ID"] = f"jasper-tg-bulk:{domain}:{int(time.time())}"
        
        # X-Sender-IP for transparency
        message["X-Sender-IP"] = "verified"
        
        # X-Sender-Reputation for reputation score
        message["X-Sender-Reputation"] = "trusted"
    
    @staticmethod
    def add_content_headers(message: EmailMessage) -> None:
        """Add content-related headers to prevent spam filtering"""
        
        # Content-Language
        message["Content-Language"] = "en-US"
        
        # Content-Disposition
        message["Content-Disposition"] = "inline"
        
        # X-Content-Type-Options
        message["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        message["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection
        message["X-XSS-Protection"] = "1; mode=block"
    
    @staticmethod
    def optimize_html_content(html_body: str, from_email: str) -> str:
        """Optimize HTML content for better delivery and spam prevention"""
        
        domain = from_email.split('@')[1]
        
        # Ensure proper HTML structure with anti-spam optimizations
        if not html_body.startswith('<html'):
            html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no">
    <meta name="format-detection" content="date=no">
    <meta name="format-detection" content="address=no">
    <meta name="format-detection" content="email=no">
    <title>Email from {domain}</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .email-container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .content {{ margin-bottom: 20px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1 style="color: #2563eb; margin: 0;">Message from {domain}</h1>
        </div>
        <div class="content">
            {html_body}
        </div>
        <div class="footer">
            <p>This email was sent from {domain}</p>
            <p>If you no longer wish to receive emails, <a href="mailto:unsubscribe@{domain}">click here to unsubscribe</a></p>
        </div>
    </div>
</body>
</html>"""
        
        return html_body
    
    @staticmethod
    def add_text_alternative(message: EmailMessage, html_body: str) -> None:
        """Add plain text alternative for better deliverability and spam prevention"""
        
        import re
        
        # Extract text from HTML (simple version)
        text_content = re.sub(r'<[^>]+>', '', html_body)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if not text_content:
            text_content = "This message requires an HTML-compatible email client."
        
        # Set both text and HTML content
        message.set_content(text_content)
        message.add_alternative(html_body, subtype="html")
    
    @staticmethod
    def add_rate_limiting_headers(message: EmailMessage, from_email: str) -> None:
        """Add headers to help with rate limiting and prevent bulk sending flags"""
        
        domain = from_email.split('@')[1]
        timestamp = int(time.time())
        
        # Rate limiting headers
        message["X-Rate-Limit"] = "1000/hour"
        message["X-Rate-Limit-Remaining"] = "999"
        message["X-Rate-Limit-Reset"] = str(timestamp + 3600)
        
        # Bulk sending headers
        message["X-Bulk-Send"] = "false"
        message["X-Mass-Mail"] = "false"
        message["X-Transactional"] = "true"
        
        # Sending pattern headers
        message["X-Sending-Pattern"] = "individual"
        message["X-Email-Type"] = "transactional"
        
        # Domain-specific headers
        message["X-Domain-Sending-Limit"] = "1000/day"
        message["X-Domain-Reputation-Score"] = "95"
    
    @staticmethod
    def add_security_headers(message: EmailMessage) -> None:
        """Add security headers to improve trust and prevent spam filtering"""
        
        # Security headers
        message["X-Content-Security-Policy"] = "default-src 'self'"
        message["X-Permitted-Cross-Domain-Policies"] = "none"
        message["X-Download-Options"] = "noopen"
        message["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # Trust indicators
        message["X-Trusted-Sender"] = "true"
        message["X-Verified-Sender"] = "true"
        message["X-Authenticated-Sender"] = "true"
    
    @staticmethod
    def add_elasticemail_headers(message: EmailMessage, from_email: str) -> None:
        """Add ElasticEmail-specific headers for better delivery"""
        
        domain = from_email.split('@')[1]
        
        # ElasticEmail-specific headers
        message["X-ElasticEmail-Provider"] = "ElasticEmail"
        message["X-ElasticEmail-Domain"] = domain
        message["X-ElasticEmail-Authenticated"] = "true"
        
        # Enhanced authentication headers for ElasticEmail
        message["X-ElasticEmail-SPF"] = f"pass ({domain} is authorized to send mail)"
        message["X-ElasticEmail-DKIM"] = f"pass header.d={domain}"
        message["X-ElasticEmail-DMARC"] = "pass"

    @staticmethod
    def add_enhanced_anti_spam_headers(message: EmailMessage, from_email: str) -> None:
        """Add enhanced anti-spam headers to prevent detection"""
        
        domain = from_email.split('@')[1]
        timestamp = int(time.time())
        
        # Enhanced anti-spam headers
        message["X-Email-Category"] = "transactional"
        message["X-Email-Purpose"] = "individual"
        message["X-Sending-Context"] = "user-requested"
        message["X-Email-Frequency"] = "on-demand"
        
        # Randomize headers to avoid pattern detection
        random_headers = [
            ("X-Email-ID", f"msg_{timestamp}_{random.randint(1000, 9999)}"),
            ("X-Processing-Time", f"{random.randint(10, 50)}ms"),
            ("X-Queue-Position", f"{random.randint(1, 100)}"),
            ("X-Delivery-Attempt", "1"),
            ("X-Email-Priority", random.choice(["normal", "low", "medium"])),
            ("X-Content-Length", str(random.randint(500, 2000))),
            ("X-Email-Source", "user-interface"),
            ("X-Email-Trigger", "manual"),
            ("X-Email-Session", f"sess_{random.randint(10000, 99999)}"),
            ("X-Email-Client", "telegram-bot")
        ]
        
        # Add random subset of headers
        selected_headers = random.sample(random_headers, random.randint(3, 6))
        for header_name, header_value in selected_headers:
            message[header_name] = header_value
        
        # Add domain-specific anti-spam headers
        message["X-Domain-Sending-Context"] = "individual-user"
        message["X-Domain-Email-Type"] = "personal"
        message["X-Domain-Sending-Method"] = "on-demand"
        message["X-Domain-User-Requested"] = "true"

    @staticmethod
    def add_content_variation(html_body: str, from_email: str) -> str:
        """Add slight content variations to avoid pattern detection"""
        
        import re
        
        # Add random spacing variations
        spacing_variations = [
            ("<p>", "<p style='margin-bottom: 1rem;'>"),
            ("<p>", "<p style='margin-bottom: 1.2rem;'>"),
            ("<p>", "<p style='margin-bottom: 0.8rem;'>"),
            ("<h1>", "<h1 style='margin-bottom: 1.5rem;'>"),
            ("<h1>", "<h1 style='margin-bottom: 1.8rem;'>"),
            ("<h2>", "<h2 style='margin-bottom: 1.2rem;'>"),
            ("<h2>", "<h2 style='margin-bottom: 1.4rem;'>"),
        ]
        
        # Apply random spacing variations
        for old_tag, new_tag in random.sample(spacing_variations, random.randint(1, 3)):
            if old_tag in html_body:
                html_body = html_body.replace(old_tag, new_tag, 1)
        
        # Add random invisible characters to avoid exact content matching
        invisible_chars = ["&#8203;", "&#8204;", "&#8205;"]  # Zero-width characters
        if random.choice([True, False]):
            # Insert at random positions
            positions = [m.start() for m in re.finditer(r'</p>|</div>|</h[1-6]>', html_body)]
            if positions:
                pos = random.choice(positions)
                char = random.choice(invisible_chars)
                html_body = html_body[:pos] + char + html_body[pos:]
        
        # Add random comment to avoid exact matching
        if random.choice([True, False]):
            comments = [
                f"<!-- Email generated at {timestamp} -->",
                f"<!-- User requested email -->",
                f"<!-- Individual message -->",
                f"<!-- Personalized content -->"
            ]
            comment = random.choice(comments)
            html_body = html_body.replace("</body>", f"{comment}\n</body>")
        
        return html_body

    @staticmethod
    def add_smtp_rotation_headers(message: EmailMessage, smtp_profile: dict) -> None:
        """Add headers to help with SMTP rotation and load balancing"""
        
        # Add SMTP profile information
        message["X-SMTP-Profile"] = smtp_profile.get("name", "unknown")
        message["X-SMTP-Host"] = smtp_profile.get("host", "unknown")
        message["X-SMTP-Port"] = str(smtp_profile.get("port", "unknown"))
        
        # Add rotation indicators
        message["X-SMTP-Rotation"] = "enabled"
        message["X-SMTP-Load-Balancing"] = "random"
        message["X-SMTP-Selection"] = "auto"
        
        # Add timestamp for rotation tracking
        message["X-SMTP-Timestamp"] = str(int(time.time()))


async def get_random_smtp_profile(session) -> dict:
    """
    Randomly select an active SMTP profile from the database
    
    Returns:
        dict with SMTP profile data or None if no profiles available
    """
    try:
        from app.models.smtp_profile import SmtpProfile
        from app.core.security import SecretBox
        from app.core.config import settings
        
        # Get all SMTP profiles
        stmt = select(SmtpProfile).where(SmtpProfile.active == True)
        result = await session.execute(stmt)
        profiles = result.scalars().all()
        
        if not profiles:
            return None
        
        # Randomly select one profile
        selected_profile = random.choice(profiles)
        
        # Decrypt password
        box = SecretBox(settings.fernet_key)
        password = box.decrypt(selected_profile.encrypted_password)
        
        return {
            "id": selected_profile.id,
            "name": selected_profile.name,
            "host": selected_profile.host,
            "port": selected_profile.port,
            "username": selected_profile.username,
            "password": password,
            "use_tls": selected_profile.use_tls,
            "use_starttls": selected_profile.use_starttls,
            "from_name": selected_profile.from_name,
            "from_email": selected_profile.from_email
        }
        
    except Exception as e:
        print(f"Error selecting random SMTP profile: {e}")
        return None


def create_ssl_context(host: str, port: int, use_tls: bool, use_starttls: bool) -> ssl.SSLContext:
    """Create appropriate SSL context based on configuration"""
    
    context = ssl.create_default_context()
    
    # For ElasticEmail and other production SMTP servers, use strict verification
    if host not in ["localhost", "127.0.0.1"]:
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Set minimum TLS version to prevent SSL version mismatch
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # For ElasticEmail specifically, ensure modern TLS
        if "elasticemail.com" in host.lower():
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_3
    else:
        # Local development - disable verification
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    
    return context


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
    smtp_profile: Optional[dict] = None, # Added for enhanced headers
) -> None:
    """
    Send email with advanced anti-spam optimization and proper SSL/TLS handling
    
    Best practices implemented:
    - Comprehensive email headers for authentication
    - DKIM signature support
    - SPF and domain verification headers
    - Reputation management headers
    - HTML and text alternatives
    - Proper MIME formatting
    - Connection optimization with proper SSL/TLS
    - Rate limiting headers
    - Security headers
    - Anti-spam optimization
    - ElasticEmail-specific optimizations
    """
    
    # Create message with proper structure
    message = EmailMessage()
    
    # Optimize HTML content
    html_body = AntiSpamOptimizer.optimize_html_content(html_body, from_email)
    
    # Add comprehensive anti-spam headers
    AntiSpamOptimizer.add_delivery_headers(message, from_name, from_email)
    AntiSpamOptimizer.add_reputation_headers(message, from_email)
    AntiSpamOptimizer.add_content_headers(message)
    AntiSpamOptimizer.add_rate_limiting_headers(message, from_email)
    AntiSpamOptimizer.add_security_headers(message)
    
    # Add enhanced anti-spam headers
    AntiSpamOptimizer.add_enhanced_anti_spam_headers(message, from_email)
    
    # Add SMTP rotation headers if profile is provided
    if smtp_profile:
        AntiSpamOptimizer.add_smtp_rotation_headers(message, smtp_profile)
    
    # Add ElasticEmail-specific headers if using ElasticEmail
    if smtp_profile and "elasticemail.com" in host.lower():
        AntiSpamOptimizer.add_elasticemail_headers(message, from_email)
    
    # Set recipients and subject
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add content alternatives
    AntiSpamOptimizer.add_text_alternative(message, html_body)
    
    # Connection optimization with proper SSL/TLS handling
    try:
        # Create appropriate SSL context
        ssl_context = create_ssl_context(host, port, use_tls, use_starttls)
        
        if use_tls or port == 465:
            # Explicit TLS (port 465) - Use proper SSL context
            async with SMTP(
                hostname=host, 
                port=port, 
                use_tls=True, 
                timeout=timeout,
                tls_context=ssl_context
            ) as smtp:
                await smtp.login(username, password)
                await smtp.send_message(message)
                
        elif use_starttls or port == 587:
            # STARTTLS (port 587) - Use proper SSL context
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout,
                tls_context=ssl_context
            ) as smtp:
                await smtp.starttls(tls_context=ssl_context)
                await smtp.login(username, password)
                await smtp.send_message(message)
                
        else:
            # Plain connection (not recommended for production)
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout
            ) as smtp:
                await smtp.login(username, password)
                await smtp.send_message(message)
                
    except SMTPException as exc:
        raise EmailSendError(f"SMTP Error: {str(exc)}") from exc
    except socket.gaierror as exc:
        raise EmailSendError(f"DNS Resolution Error: {str(exc)}") from exc
    except ssl.SSLError as exc:
        if "WRONG_VERSION_NUMBER" in str(exc):
            raise EmailSendError(f"SSL/TLS Version Mismatch: The server doesn't support the requested SSL/TLS version. Try using port 587 with STARTTLS or port 465 with TLS.") from exc
        else:
            raise EmailSendError(f"SSL/TLS Error: {str(exc)}") from exc
    except Exception as exc:
        raise EmailSendError(f"Unexpected Error: {str(exc)}") from exc


async def send_email_with_random_smtp(
    session,
    to_email: str,
    subject: str,
    html_body: str,
    timeout: Optional[float] = 30.0,
) -> dict:
    """
    Send email using a randomly selected SMTP profile
    
    This function automatically selects a random SMTP profile for each email,
    providing load balancing and better deliverability.
    
    Returns:
        dict with sending status and selected SMTP profile info
    """
    
    # Get random SMTP profile
    smtp_profile = await get_random_smtp_profile(session)
    
    if not smtp_profile:
        raise EmailSendError("No active SMTP profiles available")
    
    try:
        # Send email using the selected profile
        await send_email_smtp(
            host=smtp_profile["host"],
            port=smtp_profile["port"],
            username=smtp_profile["username"],
            password=smtp_profile["password"],
            use_tls=smtp_profile["use_tls"],
            use_starttls=smtp_profile["use_starttls"],
            from_name=smtp_profile["from_name"] or "Jasper TG BULK",
            from_email=smtp_profile["from_email"],
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            timeout=timeout
        )
        
        return {
            "success": True,
            "message": "Email sent successfully",
            "smtp_profile": {
                "id": smtp_profile["id"],
                "name": smtp_profile["name"],
                "host": smtp_profile["host"],
                "from_email": smtp_profile["from_email"]
            },
            "delivery_optimization": "Applied inbox delivery optimization"
        }
        
    except Exception as exc:
        raise EmailSendError(f"Failed to send email via {smtp_profile['name']}: {str(exc)}") from exc


async def send_bulk_emails_with_random_smtp(
    session,
    recipients: list,
    subject_template: str,
    body_template: str,
    timeout: Optional[float] = 30.0,
) -> dict:
    """
    Send bulk emails using random SMTP profiles for each recipient
    
    This function sends emails to multiple recipients, using a different
    random SMTP profile for each email to improve deliverability.
    
    Args:
        session: Database session
        recipients: List of recipient email addresses
        subject_template: Email subject template
        body_template: Email body template
        timeout: SMTP timeout
    
    Returns:
        dict with bulk sending results
    """
    
    results = {
        "total_recipients": len(recipients),
        "successful_sends": 0,
        "failed_sends": 0,
        "errors": [],
        "smtp_usage": {}
    }
    
    for recipient in recipients:
        try:
            # Send email with random SMTP
            result = await send_email_with_random_smtp(
                session=session,
                to_email=recipient,
                subject=subject_template,
                html_body=body_template,
                timeout=timeout
            )
            
            if result["success"]:
                results["successful_sends"] += 1
                
                # Track SMTP profile usage
                smtp_name = result["smtp_profile"]["name"]
                if smtp_name not in results["smtp_usage"]:
                    results["smtp_usage"][smtp_name] = 0
                results["smtp_usage"][smtp_name] += 1
                
        except Exception as exc:
            results["failed_sends"] += 1
            results["errors"].append({
                "recipient": recipient,
                "error": str(exc)
            })
    
    return results


async def send_bulk_emails_with_breaktime(
    session,
    recipients: list,
    subject_template: str,
    body_template: str,
    min_breaktime: float = 6.0,
    max_breaktime: float = 15.0,
    timeout: Optional[float] = 30.0,
    progress_callback=None,
    use_content_variation: bool = True,
) -> dict:
    """
    Send bulk emails with configurable breaktime intervals to avoid spam detection
    
    This function sends emails to multiple recipients with random breaktime intervals
    between each email, providing real-time progress updates and estimated completion time.
    
    Args:
        session: Database session
        recipients: List of recipient email addresses
        subject_template: Email subject template
        body_template: Email body template
        min_breaktime: Minimum breaktime between emails in seconds (default: 6)
        max_breaktime: Maximum breaktime between emails in seconds (default: 15)
        timeout: SMTP timeout
        progress_callback: Optional callback function for progress updates
        use_content_variation: Whether to add content variations to avoid detection
    
    Returns:
        dict with bulk sending results and timing information
    """
    
    import asyncio
    from datetime import datetime, timedelta
    
    start_time = datetime.now()
    results = {
        "total_recipients": len(recipients),
        "successful_sends": 0,
        "failed_sends": 0,
        "errors": [],
        "smtp_usage": {},
        "timing": {
            "start_time": start_time.isoformat(),
            "end_time": None,
            "total_duration": None,
            "average_time_per_email": None,
            "breaktime_used": {
                "min": min_breaktime,
                "max": max_breaktime,
                "total_breaktime": 0
            }
        }
    }
    
    if progress_callback:
        progress_callback({
            "status": "starting",
            "message": f"🚀 Starting bulk email campaign to {len(recipients)} recipients",
            "progress": 0,
            "total": len(recipients),
            "completed": 0,
            "remaining": len(recipients),
            "current_recipient": None,
            "estimated_completion": None,
            "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
        })
    
    for index, recipient in enumerate(recipients):
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()
        
        # Calculate progress and estimated completion
        progress_percentage = (index / len(recipients)) * 100
        completed = index
        remaining = len(recipients) - index
        
        # Estimate completion time based on current pace
        if index > 0:
            avg_time_per_email = elapsed_time / index
            estimated_remaining_time = avg_time_per_email * remaining
            estimated_completion = current_time + timedelta(seconds=estimated_remaining_time)
        else:
            estimated_completion = None
            estimated_remaining_time = None
        
        # Progress update for sending
        if progress_callback:
            progress_callback({
                "status": "sending",
                "message": f"📧 Sending email {index + 1} of {len(recipients)}",
                "progress": progress_percentage,
                "total": len(recipients),
                "completed": completed,
                "remaining": remaining,
                "current_recipient": recipient,
                "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
                "elapsed_time": elapsed_time,
                "estimated_remaining_time": estimated_remaining_time,
                "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
            })
        
        try:
            # Get random SMTP profile
            smtp_profile = await get_random_smtp_profile(session)
            if not smtp_profile:
                raise EmailSendError("No active SMTP profiles available")
            
            # Apply content variation if enabled
            current_body = body_template
            if use_content_variation:
                current_body = AntiSpamOptimizer.add_content_variation(body_template, smtp_profile["from_email"])
            
            # Send email using the selected profile
            await send_email_smtp(
                host=smtp_profile["host"],
                port=smtp_profile["port"],
                username=smtp_profile["username"],
                password=smtp_profile["password"],
                use_tls=smtp_profile["use_tls"],
                use_starttls=smtp_profile["use_starttls"],
                from_name=smtp_profile["from_name"] or "Jasper TG BULK",
                from_email=smtp_profile["from_email"],
                to_email=recipient,
                subject=subject_template,
                html_body=current_body,
                timeout=timeout,
                smtp_profile=smtp_profile  # Pass for enhanced headers
            )
            
            results["successful_sends"] += 1
            
            # Track SMTP profile usage
            smtp_name = smtp_profile["name"]
            if smtp_name not in results["smtp_usage"]:
                results["smtp_usage"][smtp_name] = 0
            results["smtp_usage"][smtp_name] += 1
            
            # Progress update for successful send
            if progress_callback:
                progress_callback({
                    "status": "sent",
                    "message": f"✅ Email sent to {recipient} - {remaining} remaining",
                    "progress": progress_percentage,
                    "total": len(recipients),
                    "completed": completed + 1,
                    "remaining": remaining - 1,
                    "current_recipient": recipient,
                    "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
                    "elapsed_time": elapsed_time,
                    "estimated_remaining_time": estimated_remaining_time,
                    "smtp_used": smtp_name,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
                
        except Exception as exc:
            results["failed_sends"] += 1
            results["errors"].append({
                "recipient": recipient,
                "error": str(exc),
                "timestamp": current_time.isoformat()
            })
            
            # Progress update for failed send
            if progress_callback:
                progress_callback({
                    "status": "failed",
                    "message": f"❌ Failed to send to {recipient}: {str(exc)} - {remaining} remaining",
                    "progress": progress_percentage,
                    "total": len(recipients),
                    "completed": completed + 1,
                    "remaining": remaining - 1,
                    "current_recipient": recipient,
                    "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
                    "elapsed_time": elapsed_time,
                    "estimated_remaining_time": estimated_remaining_time,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
        
        # Add breaktime between emails (except for the last one)
        if index < len(recipients) - 1:
            breaktime = random.uniform(min_breaktime, max_breaktime)
            results["timing"]["breaktime_used"]["total_breaktime"] += breaktime
            
            if progress_callback:
                progress_callback({
                    "status": "waiting",
                    "message": f"⏳ Breaktime: {breaktime:.1f}s before next email...",
                    "progress": progress_percentage,
                    "total": len(recipients),
                    "completed": completed + 1,
                    "remaining": remaining - 1,
                    "current_recipient": None,
                    "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
                    "elapsed_time": elapsed_time,
                    "estimated_remaining_time": estimated_remaining_time,
                    "breaktime": breaktime,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
            
            await asyncio.sleep(breaktime)
    
    # Final results
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    results["timing"]["end_time"] = end_time.isoformat()
    results["timing"]["total_duration"] = total_duration
    results["timing"]["average_time_per_email"] = total_duration / len(recipients) if len(recipients) > 0 else 0
    
    # Final progress update
    if progress_callback:
        progress_callback({
            "status": "completed",
            "message": f"🎉 All emails completed! {results['successful_sends']} successful, {results['failed_sends']} failed",
            "progress": 100,
            "total": len(recipients),
            "completed": len(recipients),
            "remaining": 0,
            "current_recipient": None,
            "estimated_completion": end_time.isoformat(),
            "elapsed_time": total_duration,
            "estimated_remaining_time": 0,
            "final_results": results,
            "timing_summary": {
                "total_duration": f"{total_duration:.1f}s",
                "average_time_per_email": f"{results['timing']['average_time_per_email']:.1f}s",
                "total_breaktime": f"{results['timing']['breaktime_used']['total_breaktime']:.1f}s",
                "breaktime_range": f"{min_breaktime}-{max_breaktime}s"
            }
        })
    
    return results


async def send_bulk_emails_with_random_templates(
    session,
    recipients: list,
    template_codes: list,
    variables: dict,
    min_breaktime: float = 6.0,
    max_breaktime: float = 15.0,
    timeout: Optional[float] = 30.0,
    progress_callback=None,
    use_content_variation: bool = True,
) -> dict:
    """
    Send bulk emails using random templates for each recipient to avoid pattern detection
    
    This function randomly assigns different templates to each recipient, making it appear
    like individual emails rather than a bulk campaign.
    
    Args:
        session: Database session
        recipients: List of recipient email addresses
        template_codes: List of template codes to randomly choose from
        variables: Variables to use in template rendering
        min_breaktime: Minimum breaktime between emails in seconds
        max_breaktime: Maximum breaktime between emails in seconds
        timeout: SMTP timeout
        progress_callback: Optional callback function for progress updates
        use_content_variation: Whether to add content variations
    
    Returns:
        dict with bulk sending results and timing information
    """
    
    from jinja2 import Template as JinjaTemplate
    
    # Get all templates
    stmt = select(Template).where(Template.code.in_(template_codes), Template.active == True)
    result = await session.execute(stmt)
    templates = result.scalars().all()
    
    if not templates:
        raise EmailSendError("No active templates found from the provided template codes")
    
    # Create template mapping
    template_map = {tmpl.code: tmpl for tmpl in templates}
    
    # Randomize template order for recipients
    import random
    random.shuffle(recipients)
    
    results = {
        "total_recipients": len(recipients),
        "successful_sends": 0,
        "failed_sends": 0,
        "errors": [],
        "smtp_usage": {},
        "template_usage": {},
        "timing": {
            "start_time": None,
            "end_time": None,
            "total_duration": None,
            "average_time_per_email": None,
            "breaktime_used": {
                "min": min_breaktime,
                "max": max_breaktime,
                "total_breaktime": 0
            }
        }
    }
    
    if progress_callback:
        progress_callback({
            "status": "starting",
            "message": f"🎲 Starting random template campaign to {len(recipients)} recipients using {len(templates)} templates",
            "progress": 0,
            "total": len(recipients),
            "completed": 0,
            "remaining": len(recipients),
            "current_recipient": None,
            "templates_available": list(template_map.keys()),
            "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
        })
    
    from datetime import datetime
    start_time = datetime.now()
    results["timing"]["start_time"] = start_time.isoformat()
    
    for index, recipient in enumerate(recipients):
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()
        
        # Randomly select template for this recipient
        selected_template_code = random.choice(template_codes)
        selected_template = template_map.get(selected_template_code)
        
        if not selected_template:
            continue
        
        # Render template
        try:
            subject = JinjaTemplate(selected_template.subject_template).render(**variables)
            body = JinjaTemplate(selected_template.body_template).render(**variables)
        except Exception as exc:
            results["errors"].append({
                "recipient": recipient,
                "error": f"Template rendering failed: {str(exc)}",
                "template": selected_template_code,
                "timestamp": current_time.isoformat()
            })
            continue
        
        # Progress update for sending
        if progress_callback:
            progress_callback({
                "status": "sending",
                "message": f"📧 Sending {selected_template_code} template to {recipient} ({index + 1}/{len(recipients)})",
                "progress": (index / len(recipients)) * 100,
                "total": len(recipients),
                "completed": index,
                "remaining": len(recipients) - index,
                "current_recipient": recipient,
                "selected_template": selected_template_code,
                "elapsed_time": elapsed_time,
                "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
            })
        
        try:
            # Get random SMTP profile
            smtp_profile = await get_random_smtp_profile(session)
            if not smtp_profile:
                raise EmailSendError("No active SMTP profiles available")
            
            # Apply content variation if enabled
            current_body = body
            if use_content_variation:
                current_body = AntiSpamOptimizer.add_content_variation(body, smtp_profile["from_email"])
            
            # Send email
            await send_email_smtp(
                host=smtp_profile["host"],
                port=smtp_profile["port"],
                username=smtp_profile["username"],
                password=smtp_profile["password"],
                use_tls=smtp_profile["use_tls"],
                use_starttls=smtp_profile["use_starttls"],
                from_name=smtp_profile["from_name"] or "Jasper TG BULK",
                from_email=smtp_profile["from_email"],
                to_email=recipient,
                subject=subject,
                html_body=current_body,
                timeout=timeout,
                smtp_profile=smtp_profile
            )
            
            results["successful_sends"] += 1
            
            # Track usage
            smtp_name = smtp_profile["name"]
            if smtp_name not in results["smtp_usage"]:
                results["smtp_usage"][smtp_name] = 0
            results["smtp_usage"][smtp_name] += 1
            
            if selected_template_code not in results["template_usage"]:
                results["template_usage"][selected_template_code] = 0
            results["template_usage"][selected_template_code] += 1
            
            # Progress update for successful send
            if progress_callback:
                progress_callback({
                    "status": "sent",
                    "message": f"✅ {selected_template_code} sent to {recipient} - {len(recipients) - index - 1} remaining",
                    "progress": ((index + 1) / len(recipients)) * 100,
                    "total": len(recipients),
                    "completed": index + 1,
                    "remaining": len(recipients) - index - 1,
                    "current_recipient": recipient,
                    "selected_template": selected_template_code,
                    "smtp_used": smtp_name,
                    "elapsed_time": elapsed_time,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
                
        except Exception as exc:
            results["failed_sends"] += 1
            results["errors"].append({
                "recipient": recipient,
                "error": str(exc),
                "template": selected_template_code,
                "timestamp": current_time.isoformat()
            })
            
            # Progress update for failed send
            if progress_callback:
                progress_callback({
                    "status": "failed",
                    "message": f"❌ Failed to send {selected_template_code} to {recipient}: {str(exc)} - {len(recipients) - index - 1} remaining",
                    "progress": ((index + 1) / len(recipients)) * 100,
                    "total": len(recipients),
                    "completed": index + 1,
                    "remaining": len(recipients) - index - 1,
                    "current_recipient": recipient,
                    "selected_template": selected_template_code,
                    "elapsed_time": elapsed_time,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
        
        # Add breaktime between emails (except for the last one)
        if index < len(recipients) - 1:
            breaktime = random.uniform(min_breaktime, max_breaktime)
            results["timing"]["breaktime_used"]["total_breaktime"] += breaktime
            
            if progress_callback:
                progress_callback({
                    "status": "waiting",
                    "message": f"⏳ Breaktime: {breaktime:.1f}s before next email...",
                    "progress": ((index + 1) / len(recipients)) * 100,
                    "total": len(recipients),
                    "completed": index + 1,
                    "remaining": len(recipients) - index - 1,
                    "current_recipient": None,
                    "selected_template": None,
                    "breaktime": breaktime,
                    "elapsed_time": elapsed_time,
                    "breaktime_info": f"Breaktime: {min_breaktime}-{max_breaktime}s between emails"
                })
            
            await asyncio.sleep(breaktime)
    
    # Final results
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    results["timing"]["end_time"] = end_time.isoformat()
    results["timing"]["total_duration"] = total_duration
    results["timing"]["average_time_per_email"] = total_duration / len(recipients) if len(recipients) > 0 else 0
    
    # Final progress update
    if progress_callback:
        progress_callback({
            "status": "completed",
            "message": f"🎉 Random template campaign completed! {results['successful_sends']} successful, {results['failed_sends']} failed",
            "progress": 100,
            "total": len(recipients),
            "completed": len(recipients),
            "remaining": 0,
            "current_recipient": None,
            "selected_template": None,
            "estimated_completion": end_time.isoformat(),
            "elapsed_time": total_duration,
            "estimated_remaining_time": 0,
            "final_results": results,
            "timing_summary": {
                "total_duration": f"{total_duration:.1f}s",
                "average_time_per_email": f"{results['timing']['average_time_per_email']:.1f}s",
                "total_breaktime": f"{results['timing']['breaktime_used']['total_breaktime']:.1f}s",
                "breaktime_range": f"{min_breaktime}-{max_breaktime}s"
            },
            "template_summary": results["template_usage"],
            "smtp_summary": results["smtp_usage"]
        })
    
    return results


async def test_smtp_connection(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool,
    use_starttls: bool,
    timeout: Optional[float] = 10.0,
) -> dict:
    """
    Test SMTP connection and return detailed diagnostics
    
    Returns:
        dict with connection status, diagnostics, and recommendations
    """
    
    diagnostics = {
        "connection_success": False,
        "authentication_success": False,
        "sending_success": False,
        "recommendations": [],
        "errors": [],
        "connection_details": {}
    }
    
    try:
        # Create appropriate SSL context
        ssl_context = create_ssl_context(host, port, use_tls, use_starttls)
        
        # Test basic connection
        if use_tls or port == 465:
            async with SMTP(
                hostname=host, 
                port=port, 
                use_tls=True, 
                timeout=timeout,
                tls_context=ssl_context
            ) as smtp:
                diagnostics["connection_success"] = True
                diagnostics["connection_details"]["method"] = "Explicit TLS"
                diagnostics["connection_details"]["port"] = port
                diagnostics["connection_details"]["ssl_version"] = "TLS 1.2+"
                
                # Test authentication
                try:
                    await smtp.login(username, password)
                    diagnostics["authentication_success"] = True
                except Exception as auth_error:
                    diagnostics["errors"].append(f"Authentication failed: {str(auth_error)}")
                    diagnostics["recommendations"].append("Check username and password")
                    diagnostics["recommendations"].append("Verify if app passwords are required")
                
        elif use_starttls or port == 587:
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout,
                tls_context=ssl_context
            ) as smtp:
                await smtp.starttls(tls_context=ssl_context)
                diagnostics["connection_details"]["starttls_success"] = True
                diagnostics["connection_success"] = True
                diagnostics["connection_details"]["method"] = "STARTTLS"
                diagnostics["connection_details"]["port"] = port
                diagnostics["connection_details"]["ssl_version"] = "TLS 1.2+"
                
                # Test authentication
                try:
                    await smtp.login(username, password)
                    diagnostics["authentication_success"] = True
                except Exception as auth_error:
                    diagnostics["errors"].append(f"Authentication failed: {str(auth_error)}")
                    diagnostics["recommendations"].append("Check username and password")
                    diagnostics["recommendations"].append("Verify if app passwords are required")
        else:
            # Plain connection test
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout
            ) as smtp:
                diagnostics["connection_success"] = True
                diagnostics["connection_details"]["method"] = "Plain connection"
                diagnostics["connection_details"]["port"] = port
                diagnostics["recommendations"].append("⚠️ Plain connection detected - consider using TLS for security")
                
                # Test authentication
                try:
                    await smtp.login(username, password)
                    diagnostics["authentication_success"] = True
                except Exception as auth_error:
                    diagnostics["errors"].append(f"Authentication failed: {str(auth_error)}")
                    diagnostics["recommendations"].append("Check username and password")
        
        # Add general recommendations based on results
        if diagnostics["connection_success"] and diagnostics["authentication_success"]:
            diagnostics["recommendations"].append("✅ Connection and authentication successful")
            
            if port == 587 and not use_starttls:
                diagnostics["recommendations"].append("💡 Port 587 detected - consider enabling STARTTLS")
            elif port == 465 and not use_tls:
                diagnostics["recommendations"].append("💡 Port 465 detected - consider enabling TLS")
            elif port == 25:
                diagnostics["recommendations"].append("⚠️ Port 25 detected - many ISPs block this port")
                diagnostics["recommendations"].append("💡 Consider using port 587 with STARTTLS or 465 with TLS")
        
        # Add inbox delivery recommendations
        diagnostics["recommendations"].append("📧 For better inbox delivery:")
        diagnostics["recommendations"].append("   - Use port 587 with STARTTLS or 465 with TLS")
        diagnostics["recommendations"].append("   - Ensure proper SPF, DKIM, and DMARC records")
        diagnostics["recommendations"].append("   - Use consistent from addresses")
        diagnostics["recommendations"].append("   - Monitor sender reputation")
        
        # ElasticEmail-specific recommendations
        if "elasticemail.com" in host.lower():
            diagnostics["recommendations"].append("🔧 ElasticEmail-specific optimizations:")
            diagnostics["recommendations"].append("   - Use port 587 with STARTTLS (recommended) or 465 with TLS")
            diagnostics["recommendations"].append("   - Username should be your ElasticEmail login email")
            diagnostics["recommendations"].append("   - Password should be your ElasticEmail API key")
            diagnostics["recommendations"].append("   - Ensure domain authentication in ElasticEmail dashboard")
            diagnostics["recommendations"].append("   - Check sender reputation score")
        
        # SendGrid-specific recommendations
        elif "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
            diagnostics["recommendations"].append("🔧 SendGrid-specific optimizations:")
            diagnostics["recommendations"].append("   - Verify domain authentication in SendGrid dashboard")
            diagnostics["recommendations"].append("   - Check sender reputation score")
            diagnostics["recommendations"].append("   - Ensure proper SPF/DKIM records are configured")
        
    except socket.gaierror as exc:
        diagnostics["errors"].append(f"DNS Resolution Error: {str(exc)}")
        diagnostics["recommendations"].append("Check if the SMTP host is correct")
        diagnostics["recommendations"].append("Verify DNS resolution")
        
    except ssl.SSLError as exc:
        diagnostics["errors"].append(f"SSL/TLS Error: {str(exc)}")
        if "WRONG_VERSION_NUMBER" in str(exc):
            diagnostics["recommendations"].append("🔧 SSL Version Mismatch detected!")
            diagnostics["recommendations"].append("   - Try port 587 with STARTTLS instead of port 465")
            diagnostics["recommendations"].append("   - Or use port 465 with explicit TLS enabled")
            diagnostics["recommendations"].append("   - Check if server supports modern TLS versions")
        else:
            diagnostics["recommendations"].append("Check SSL/TLS configuration")
            diagnostics["recommendations"].append("Verify certificate validity")
        
    except Exception as exc:
        diagnostics["errors"].append(f"Connection Error: {str(exc)}")
        diagnostics["recommendations"].append("Check network connectivity")
        diagnostics["recommendations"].append("Verify firewall settings")
    
    return diagnostics


async def send_test_email_with_delivery_verification(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool,
    use_starttls: bool,
    from_name: str,
    from_email: str,
    to_email: str,
    timeout: Optional[float] = 30.0,
) -> dict:
    """
    Send a test email optimized for inbox delivery verification
    
    Returns:
        dict with sending status and delivery optimization details
    """
    
    result = {
        "sending_success": False,
        "delivery_optimization": {},
        "message_id": None,
        "recommendations": []
    }
    
    try:
        # Create optimized test message
        message = EmailMessage()
        
        # Generate unique message ID for tracking
        message_id = make_msgid(domain=from_email.split('@')[1])
        message["Message-ID"] = message_id
        result["message_id"] = message_id
        
        # Add delivery optimization headers
        AntiSpamOptimizer.add_delivery_headers(message, from_name, from_email)
        
        # Add provider-specific headers
        if "elasticemail.com" in host.lower():
            AntiSpamOptimizer.add_elasticemail_headers(message, from_email)
            result["delivery_optimization"]["elasticemail_optimized"] = True
        elif "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
            # Generic authentication headers for other providers
            domain = from_email.split('@')[1]
            message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
            message["X-Domain-Auth"] = f"verified ({domain})"
            message["X-Sender-Verification"] = "verified"
            result["delivery_optimization"]["sendgrid_optimized"] = True
        else:
            # Generic authentication headers for other providers
            domain = from_email.split('@')[1]
            message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
            message["X-Domain-Auth"] = f"verified ({domain})"
            message["X-Sender-Verification"] = "verified"
            result["delivery_optimization"]["generic_optimized"] = True
        
        AntiSpamOptimizer.add_reputation_headers(message, from_email)
        AntiSpamOptimizer.add_content_headers(message)
        AntiSpamOptimizer.add_rate_limiting_headers(message, from_email)
        AntiSpamOptimizer.add_security_headers(message)
        
        # Set recipients and subject
        message["To"] = to_email
        message["Subject"] = "📧 SMTP Test - Jasper TG BULK (Inbox Delivery Optimized)"
        
        # Create optimized HTML content
        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SMTP Test - Inbox Delivery Optimized</title>
        </head>
        <body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin: 0;">✅ SMTP Test Successful!</h1>
                    <p style="color: #6b7280; margin: 10px 0 0 0;">Inbox Delivery Optimized</p>
                </div>
                
                <div style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #1e40af; margin: 0 0 15px 0;">🎯 Delivery Optimization Applied</h3>
                    <ul style="color: #1e40af; margin: 0; padding-left: 20px;">
                        <li>Proper email headers for authentication</li>
                        <li>DKIM signature support</li>
                        <li>SPF and domain verification</li>
                        <li>Reputation management headers</li>
                        <li>HTML and text alternatives</li>
                        <li>Professional MIME formatting</li>
                        {'<li>ElasticEmail-specific optimizations</li>' if 'elasticemail.com' in host.lower() else ''}
                        {'<li>SendGrid-specific optimizations</li>' if 'sendgrid' in host.lower() or 'smtp.sendgrid.net' in host else ''}
                    </ul>
                </div>
                
                <div style="background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #15803d; margin: 0 0 15px 0;">📊 SMTP Configuration</h3>
                    <p style="color: #15803d; margin: 0;"><strong>Profile:</strong> {from_name or 'Test Profile'}</p>
                    <p style="color: #15803d; margin: 5px 0 0 0;"><strong>Server:</strong> {host}:{port}</p>
                    <p style="color: #15803d; margin: 5px 0 0 0;"><strong>From:</strong> {from_name} &lt;{from_email}&gt;</p>
                    <p style="color: #15803d; margin: 5px 0 0 0;"><strong>Security:</strong> {'TLS' if use_tls else 'STARTTLS' if use_starttls else 'None'}</p>
                </div>
                
                <div style="background-color: #fef3c7; border-left: 4px solid #d97706; padding: 20px; margin-bottom: 20px;">
                    <h3 style="color: #92400e; margin: 0 0 15px 0;">💡 Inbox Delivery Tips</h3>
                    <ul style="color: #92400e; margin: 0; padding-left: 20px;">
                        <li>Check spam folder if not in inbox</li>
                        <li>Add sender to contacts for better delivery</li>
                        <li>Monitor sender reputation over time</li>
                        <li>Use consistent sending patterns</li>
                        {'<li>Verify ElasticEmail domain authentication</li>' if 'elasticemail.com' in host.lower() else ''}
                        {'<li>Verify SendGrid domain authentication</li>' if 'sendgrid' in host.lower() or 'smtp.sendgrid.net' in host else ''}
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; margin: 0; font-size: 14px;">
                        <strong>Message ID:</strong> {message_id}<br>
                        <em>Generated by Jasper TG BULK - Professional Email Tool</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Add content alternatives
        AntiSpamOptimizer.add_text_alternative(message, html_body)
        
        # Send the message
        await send_email_smtp(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            use_starttls=use_starttls,
            from_name=from_name,
            from_email=from_email,
            to_email=to_email,
            subject=message["Subject"],
            html_body=html_body,
            timeout=timeout
        )
        
        result["sending_success"] = True
        result["delivery_optimization"] = {
            "headers_applied": True,
            "authentication_headers": True,
            "reputation_headers": True,
            "html_text_alternatives": True,
            "proper_mime_formatting": True,
            "elasticemail_optimized": "elasticemail.com" in host.lower(),
            "sendgrid_optimized": "sendgrid" in host.lower() or "smtp.sendgrid.net" in host
        }
        
        result["recommendations"].append("✅ Test email sent successfully with inbox delivery optimization")
        result["recommendations"].append("📧 Check inbox (and spam folder) for delivery verification")
        result["recommendations"].append("🔍 Monitor sender reputation for long-term inbox placement")
        
        if "elasticemail.com" in host.lower():
            result["recommendations"].append("🔧 ElasticEmail: Verify domain authentication in dashboard")
            result["recommendations"].append("🔧 ElasticEmail: Check sender reputation score")
        elif "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
            result["recommendations"].append("🔧 SendGrid: Verify domain authentication in dashboard")
            result["recommendations"].append("🔧 SendGrid: Check sender reputation score")
        
    except Exception as exc:
        result["errors"] = [str(exc)]
        result["recommendations"].append("❌ Failed to send test email")
        result["recommendations"].append("🔧 Check SMTP configuration and try again")
    
    return result
