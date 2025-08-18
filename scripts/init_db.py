#!/usr/bin/env python3
"""
Database Initialization Script for Jasper TG BULK
Creates all necessary tables with proper schema
"""

import sqlite3
import os
import sys

def init_database():
    """Initialize the database with all required tables"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
    
    # Ensure data directory exists
    data_dir = os.path.dirname(db_path)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
    
    try:
        # Connect to the database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Initializing Jasper TG BULK Database...")
        print("=" * 50)
        
        # Create smtp_profiles table
        print("📧 Creating SMTP Profiles table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smtp_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                host VARCHAR(255) NOT NULL,
                port INTEGER NOT NULL DEFAULT 587,
                username VARCHAR(255) NOT NULL,
                encrypted_password VARCHAR(255) NOT NULL,
                use_tls BOOLEAN NOT NULL DEFAULT 0,
                use_starttls BOOLEAN NOT NULL DEFAULT 1,
                from_name VARCHAR(255),
                from_email VARCHAR(255) NOT NULL,
                active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ SMTP Profiles table created")
        
        # Create template table
        print("📝 Creating Templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(64) NOT NULL UNIQUE,
                subject_template VARCHAR(500) NOT NULL,
                body_template TEXT NOT NULL,
                active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Templates table created")
        
        # Create customer_allowlist table
        print("👥 Creating Customer Allowlist table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_allowlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id VARCHAR(255) NOT NULL UNIQUE,
                label VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Customer Allowlist table created")
        
        # Create admin_users table
        print("🔐 Creating Admin Users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Admin Users table created")
        
        # Insert default admin user if not exists
        print("👤 Setting up default admin user...")
        cursor.execute("""
            INSERT OR IGNORE INTO admin_users (username, hashed_password, is_active)
            VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s8uG', 1)
        """)
        print("✅ Default admin user created (username: admin, password: admin123)")
        
        # Insert sample SMTP profile if none exist
        print("📧 Setting up sample SMTP profile...")
        cursor.execute("SELECT COUNT(*) FROM smtp_profiles")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO smtp_profiles (name, host, port, username, encrypted_password, use_tls, use_starttls, from_name, from_email, active)
                VALUES ('Sample SMTP', 'smtp.gmail.com', 587, 'your-email@gmail.com', 'encrypted_password_here', 0, 1, 'Your Name', 'your-email@gmail.com', 1)
            """)
            print("✅ Sample SMTP profile created")
        else:
            print("✅ SMTP profiles already exist")
        
        # Insert sample template if none exist
        print("📝 Setting up sample template...")
        cursor.execute("SELECT COUNT(*) FROM template")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO template (code, subject_template, body_template, active)
                VALUES ('welcome_email', 'Welcome to our service!', '<h1>Welcome!</h1><p>Thank you for joining us.</p>', 1)
            """)
            print("✅ Sample template created")
        else:
            print("✅ Templates already exist")
        
        # Insert sample customer if none exist
        print("👥 Setting up sample customer...")
        cursor.execute("SELECT COUNT(*) FROM customer_allowlist")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO customer_allowlist (chat_id, label)
                VALUES ('123456789', 'Sample Customer')
            """)
            print("✅ Sample customer created")
        else:
            print("✅ Customers already exist")
        
        # Commit all changes
        conn.commit()
        
        print("=" * 50)
        print("🎉 Database initialization completed successfully!")
        print(f"📁 Database location: {db_path}")
        print("\n📋 Default credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🚀 You can now run the admin panel!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
