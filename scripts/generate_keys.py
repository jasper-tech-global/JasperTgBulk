#!/usr/bin/env python3
"""
Generate secure keys for Jasper TG BULK
"""

import secrets
import base64
from cryptography.fernet import Fernet

def generate_keys():
    """Generate secure keys for the project"""
    
    print("🔑 Generating secure keys for Jasper TG BULK...")
    print("=" * 50)
    
    # Generate SECRET_KEY (32 bytes for bcrypt)
    secret_key = secrets.token_urlsafe(32)
    print(f"🔐 SECRET_KEY: {secret_key}")
    
    # Generate FERNET_KEY (32 bytes, base64 encoded)
    fernet_key = Fernet.generate_key().decode()
    print(f"🔒 FERNET_KEY: {fernet_key}")
    
    print("\n📝 Add these to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print(f"FERNET_KEY={fernet_key}")
    
    # Create .env file if it doesn't exist
    try:
        with open('.env', 'w') as f:
            f.write(f"TELEGRAM_BOT_TOKEN=your_bot_token_here\n")
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write(f"FERNET_KEY={fernet_key}\n")
        print("\n✅ .env file created with generated keys!")
        print("⚠️  Remember to update TELEGRAM_BOT_TOKEN with your actual bot token!")
    except Exception as e:
        print(f"\n❌ Could not create .env file: {e}")
        print("Please create it manually with the keys above.")
    
    return secret_key, fernet_key

if __name__ == "__main__":
    generate_keys()
