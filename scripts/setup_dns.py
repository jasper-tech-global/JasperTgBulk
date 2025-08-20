#!/usr/bin/env python3
"""
DNS Configuration Helper for Jasper TG BULK
This script helps you set up the required DNS records to prevent emails from going to spam.
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print the script banner"""
    print("=" * 60)
    print("🔧 DNS Configuration Helper - Jasper TG BULK")
    print("=" * 60)
    print()


def get_domain_info():
    """Get domain information from user"""
    print("📧 Enter your domain information:")
    print()
    
    domain = input("Domain (e.g., example.com): ").strip()
    if not domain:
        print("❌ Domain is required!")
        sys.exit(1)
    
    # Remove http/https if user included them
    domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
    
    email_provider = input("Email provider (gmail/sendgrid/outlook/custom): ").strip().lower()
    
    return domain, email_provider


def generate_spf_record(domain, email_provider):
    """Generate SPF record based on email provider"""
    if email_provider == "gmail":
        return f"v=spf1 include:_spf.google.com ~all"
    elif email_provider == "sendgrid":
        return f"v=spf1 include:sendgrid.net ~all"
    elif email_provider == "outlook":
        return f"v=spf1 include:spf.protection.outlook.com ~all"
    else:
        return f"v=spf1 include:_spf.{domain} ~all"


def generate_dkim_record(domain, email_provider):
    """Generate DKIM record based on email provider"""
    if email_provider == "gmail":
        return f"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC4Fgtd/O8lnKv1kaAcUWz7C2/Tp3gp/agmvm+WlUaRf60GdGS9bK1lsQ+rErpa8fdfuJcXZfjyqDQ1kwBv4cOjCa1fqnOGF6vRj3sFOPmFdBlBZRyDuAXDnCMtMKxLxC+byJ7X4i5eCYqCTytb3qaztGXdBv1ucRZgLb37LQIDAQAB"
    elif email_provider == "sendgrid":
        return f"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC4Fgtd/O8lnKv1kaAcUWz7C2/Tp3gp/agmvm+WlUaRf60GdGS9bK1lsQ+rErpa8fdfuJcXZfjyqDQ1kwBv4cOjCa1fqnOGF6vRj3sFOPmFdBlBZRyDuAXDnCMtMKxLxC+byJ7X4i5eCYqCTytb3qaztGXdBv1ucRZgLb37LQIDAQAB"
    elif email_provider == "outlook":
        return f"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC4Fgtd/O8lnKv1kaAcUWz7C2/Tp3gp/agmvm+WlUaRf60GdGS9bK1lsQ+rErpa8fdfuJcXZfjyqDQ1kwBv4cOjCa1fqnOGF6vRj3sFOPmFdBlBZRyDuAXDnCMtMKxLxC+byJ7X4i5eCYqCTytb3qaztGXdBv1ucRZgLb37LQIDAQAB"
    else:
        return f"v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE"


def generate_dmarc_record(domain):
    """Generate DMARC record"""
    return f"v=DMARC1; p=quarantine; rua=mailto:dmarc@{domain}; ruf=mailto:dmarc@{domain}; sp=quarantine; adkim=r; aspf=r;"


def print_dns_records(domain, email_provider):
    """Print the DNS records that need to be configured"""
    print("\n" + "=" * 60)
    print("📋 DNS Records to Add to Your Domain")
    print("=" * 60)
    print()
    
    print("🔐 Add these records in your domain's DNS settings:")
    print()
    
    # SPF Record
    spf_value = generate_spf_record(domain, email_provider)
    print("1️⃣ SPF Record (TXT):")
    print(f"   Name: @ (or {domain})")
    print(f"   Value: {spf_value}")
    print()
    
    # DKIM Record
    dkim_value = generate_dkim_record(domain, email_provider)
    dkim_name = "default._domainkey" if email_provider != "sendgrid" else "s1._domainkey"
    print("2️⃣ DKIM Record (TXT):")
    print(f"   Name: {dkim_name}")
    print(f"   Value: {dkim_value}")
    print()
    
    # DMARC Record
    dmarc_value = generate_dmarc_record(domain)
    print("3️⃣ DMARC Record (TXT):")
    print(f"   Name: _dmarc")
    print(f"   Value: {dmarc_value}")
    print()
    
    print("⚠️  IMPORTANT NOTES:")
    print("   - These are example records - you may need to customize them")
    print("   - For Gmail: Use the exact SPF record shown above")
    print("   - For SendGrid: Get your actual DKIM key from SendGrid dashboard")
    print("   - For custom providers: Contact your email provider for exact records")
    print()


def print_smtp_configuration(domain, email_provider):
    """Print SMTP configuration recommendations"""
    print("\n" + "=" * 60)
    print("📧 SMTP Configuration Recommendations")
    print("=" * 60)
    print()
    
    if email_provider == "gmail":
        print("📮 Gmail/Google Workspace Configuration:")
        print("   Host: smtp.gmail.com")
        print("   Port: 587")
        print("   Security: STARTTLS")
        print("   Username: your-email@gmail.com")
        print("   Password: App Password (NOT regular password)")
        print()
        print("💡 To get an App Password:")
        print("   1. Enable 2FA on your Google account")
        print("   2. Go to Security > App passwords")
        print("   3. Generate password for 'Mail'")
        print()
        
    elif email_provider == "sendgrid":
        print("📮 SendGrid Configuration:")
        print("   Host: smtp.sendgrid.net")
        print("   Port: 587")
        print("   Security: STARTTLS")
        print("   Username: apikey")
        print("   Password: Your SendGrid API Key")
        print()
        print("💡 SendGrid Setup:")
        print("   1. Create SendGrid account")
        print("   2. Verify your domain")
        print("   3. Get API key from Settings > API Keys")
        print()
        
    elif email_provider == "outlook":
        print("📮 Outlook/Office 365 Configuration:")
        print("   Host: smtp-mail.outlook.com")
        print("   Port: 587")
        print("   Security: STARTTLS")
        print("   Username: your-email@outlook.com")
        print("   Password: Your password")
        print()
        
    else:
        print("📮 Custom Email Provider:")
        print("   Contact your email provider for:")
        print("   - SMTP host and port")
        print("   - Security settings (TLS/STARTTLS)")
        print("   - Authentication requirements")
        print("   - SPF/DKIM records")
        print()


def print_testing_steps():
    """Print testing and verification steps"""
    print("\n" + "=" * 60)
    print("🧪 Testing & Verification Steps")
    print("=" * 60)
    print()
    
    print("1️⃣ Test DNS Records:")
    print("   - Use MXToolbox SPF Checker: https://mxtoolbox.com/spf.aspx")
    print("   - Use DKIM Core: https://dkimcore.org/tools/")
    print("   - Use DMARC Analyzer: https://dmarc.postmarkapp.com/")
    print()
    
    print("2️⃣ Test SMTP Connection:")
    print("   - Use the 'Test Connection' button in your admin panel")
    print("   - Verify authentication works")
    print("   - Check for any error messages")
    print()
    
    print("3️⃣ Send Test Email:")
    print("   - Send test email to yourself")
    print("   - Check if it goes to inbox or spam")
    print("   - View email headers for authentication results")
    print()
    
    print("4️⃣ Monitor Deliverability:")
    print("   - Check spam folder regularly")
    print("   - Monitor bounce rates")
    print("   - Track sender reputation")
    print()


def print_best_practices():
    """Print best practices for avoiding spam"""
    print("\n" + "=" * 60)
    print("✅ Best Practices to Avoid Spam")
    print("=" * 60)
    print()
    
    print("📊 Sending Strategy:")
    print("   - Start with 10-20 emails per day")
    print("   - Increase volume gradually (20% weekly)")
    print("   - Send at consistent times")
    print("   - Focus on quality over quantity")
    print()
    
    print("📝 Content Guidelines:")
    print("   - Avoid spam trigger words (Free!, Act now, etc.)")
    print("   - Use personalization when possible")
    print("   - Include unsubscribe links")
    print("   - Keep HTML simple and clean")
    print()
    
    print("🔒 Security & Authentication:")
    print("   - Always use TLS/STARTTLS")
    print("   - Use ports 587 or 465 (avoid port 25)")
    print("   - Ensure from_email matches your domain")
    print("   - Monitor sender reputation")
    print()


def main():
    """Main function"""
    try:
        print_banner()
        
        domain, email_provider = get_domain_info()
        
        print_dns_records(domain, email_provider)
        print_smtp_configuration(domain, email_provider)
        print_testing_steps()
        print_best_practices()
        
        print("\n" + "=" * 60)
        print("🎉 DNS Configuration Guide Complete!")
        print("=" * 60)
        print()
        print("📋 Next Steps:")
        print("   1. Add the DNS records to your domain")
        print("   2. Configure SMTP profiles in admin panel")
        print("   3. Test connections and send test emails")
        print("   4. Monitor deliverability and adjust as needed")
        print()
        print("📚 For more help, see ANTI_SPAM_GUIDE.md")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
