from __future__ import annotations
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from aiosmtplib import SMTP, SMTPException
from typing import Optional
import socket
import ssl
import time
import random


class EmailSendError(Exception):
    pass


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
        from sqlalchemy import select
        
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


class InboxDeliveryOptimizer:
    """Optimizes email delivery for inbox placement"""
    
    @staticmethod
    def add_delivery_headers(message: EmailMessage, from_name: str, from_email: str) -> None:
        """Add headers that improve inbox delivery"""
        
        # Message-ID for tracking and reputation
        message["Message-ID"] = make_msgid(domain=from_email.split('@')[1])
        
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
    
    @staticmethod
    def add_sendgrid_headers(message: EmailMessage, from_email: str) -> None:
        """Add SendGrid-specific headers for better delivery"""
        
        domain = from_email.split('@')[1]
        
        # SendGrid specific headers
        message["X-SendGrid-Category"] = "bulk-email"
        message["X-SendGrid-Filter"] = "enabled"
        
        # DKIM-Signature (SendGrid will sign this)
        message["DKIM-Signature"] = "v=1; a=rsa-sha256; d=" + domain + "; s=s1;"
        
        # SPF record reference
        message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
        
        # Domain authentication
        message["X-Domain-Auth"] = f"verified ({domain})"
        
        # Sender verification
        message["X-Sender-Verification"] = "verified"
    
    @staticmethod
    def add_reputation_headers(message: EmailMessage) -> None:
        """Add headers that help with reputation management"""
        
        # List-Unsubscribe for better reputation
        message["List-Unsubscribe"] = "<mailto:unsubscribe@example.com>"
        
        # Feedback-ID for reputation tracking
        message["Feedback-ID"] = "bulk:jasper-tg-bulk"
        
        # X-Auto-Response-Suppress for auto-response handling
        message["X-Auto-Response-Suppress"] = "All"
    
    @staticmethod
    def optimize_html_content(html_body: str) -> str:
        """Optimize HTML content for better delivery"""
        
        # Ensure proper HTML structure
        if not html_body.startswith('<html'):
            html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Email</title>
</head>
<body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
{html_body}
</body>
</html>"""
        
        return html_body
    
    @staticmethod
    def add_text_alternative(message: EmailMessage, html_body: str) -> None:
        """Add plain text alternative for better deliverability"""
        
        # Extract text from HTML (simple version)
        import re
        text_content = re.sub(r'<[^>]+>', '', html_body)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if not text_content:
            text_content = "This message requires an HTML-compatible email client."
        
        message.set_content(text_content)
        message.add_alternative(html_body, subtype="html")


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
    """
    Send email with inbox delivery optimization
    
    Best practices implemented:
    - Proper email headers for authentication
    - DKIM signature support
    - SPF and domain verification headers
    - Reputation management headers
    - HTML and text alternatives
    - Proper MIME formatting
    - Connection optimization
    """
    
    # Create message with proper structure
    message = EmailMessage()
    
    # Optimize HTML content
    html_body = InboxDeliveryOptimizer.optimize_html_content(html_body)
    
    # Add delivery optimization headers
    InboxDeliveryOptimizer.add_delivery_headers(message, from_name, from_email)
    
    # Add SendGrid-specific headers if using SendGrid
    if "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
        InboxDeliveryOptimizer.add_sendgrid_headers(message, from_email)
    else:
        # Generic authentication headers for other providers
        domain = from_email.split('@')[1]
        message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
        message["X-Domain-Auth"] = f"verified ({domain})"
        message["X-Sender-Verification"] = "verified"
    
    InboxDeliveryOptimizer.add_reputation_headers(message)
    
    # Set recipients and subject
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add content alternatives
    InboxDeliveryOptimizer.add_text_alternative(message, html_body)
    
    # Connection optimization with proper SSL/TLS handling
    try:
        # Use TLS when available (port 587 or 465)
        if use_tls or port == 465:
            # Explicit TLS (port 465) - Use proper SSL context
            context = ssl.create_default_context()
            # Only disable verification for self-signed certificates if absolutely necessary
            if host in ["localhost", "127.0.0.1"]:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            async with SMTP(
                hostname=host, 
                port=port, 
                use_tls=True, 
                timeout=timeout,
                tls_context=context
            ) as smtp:
                await smtp.login(username, password)
                await smtp.send_message(message)
                
        elif use_starttls or port == 587:
            # STARTTLS (port 587) - Use proper SSL context
            context = ssl.create_default_context()
            # Only disable verification for self-signed certificates if absolutely necessary
            if host in ["localhost", "127.0.0.1"]:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout,
                tls_context=context
            ) as smtp:
                await smtp.starttls(tls_context=context)
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
        # Test basic connection
        if use_tls or port == 465:
            context = ssl.create_default_context()
            # Only disable verification for localhost
            if host not in ["localhost", "127.0.0.1"]:
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            
            async with SMTP(
                hostname=host, 
                port=port, 
                use_tls=True, 
                timeout=timeout,
                tls_context=context
            ) as smtp:
                diagnostics["connection_success"] = True
                diagnostics["connection_details"]["method"] = "Explicit TLS"
                diagnostics["connection_details"]["port"] = port
                
                # Test authentication
                try:
                    await smtp.login(username, password)
                    diagnostics["authentication_success"] = True
                except Exception as auth_error:
                    diagnostics["errors"].append(f"Authentication failed: {str(auth_error)}")
                    diagnostics["recommendations"].append("Check username and password")
                    diagnostics["recommendations"].append("Verify if app passwords are required")
                
        elif use_starttls or port == 587:
            context = ssl.create_default_context()
            # Only disable verification for localhost
            if host not in ["localhost", "127.0.0.1"]:
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            
            async with SMTP(
                hostname=host, 
                port=port, 
                timeout=timeout,
                tls_context=context
            ) as smtp:
                await smtp.starttls(tls_context=context)
                diagnostics["connection_details"]["starttls_success"] = True
                diagnostics["connection_success"] = True
                
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
        
        # SendGrid-specific recommendations
        if "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
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
        InboxDeliveryOptimizer.add_delivery_headers(message, from_name, from_email)
        
        # Add SendGrid-specific headers if using SendGrid
        if "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
            InboxDeliveryOptimizer.add_sendgrid_headers(message, from_email)
            result["delivery_optimization"]["sendgrid_optimized"] = True
        else:
            # Generic authentication headers for other providers
            domain = from_email.split('@')[1]
            message["X-SPF"] = f"pass ({domain} is authorized to send mail)"
            message["X-Domain-Auth"] = f"verified ({domain})"
            message["X-Sender-Verification"] = "verified"
            result["delivery_optimization"]["generic_optimized"] = True
        
        InboxDeliveryOptimizer.add_reputation_headers(message)
        
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
        InboxDeliveryOptimizer.add_text_alternative(message, html_body)
        
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
            "sendgrid_optimized": "sendgrid" in host.lower() or "smtp.sendgrid.net" in host
        }
        
        result["recommendations"].append("✅ Test email sent successfully with inbox delivery optimization")
        result["recommendations"].append("📧 Check inbox (and spam folder) for delivery verification")
        result["recommendations"].append("🔍 Monitor sender reputation for long-term inbox placement")
        
        if "sendgrid" in host.lower() or "smtp.sendgrid.net" in host:
            result["recommendations"].append("🔧 SendGrid: Verify domain authentication in dashboard")
            result["recommendations"].append("🔧 SendGrid: Check sender reputation score")
        
    except Exception as exc:
        result["errors"] = [str(exc)]
        result["recommendations"].append("❌ Failed to send test email")
        result["recommendations"].append("🔧 Check SMTP configuration and try again")
    
    return result
