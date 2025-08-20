#!/usr/bin/env python3
"""
Database Migration Script for Jasper TG BULK
Adds missing smtp_profile_id column to template table
"""

import sqlite3
import os
import sys

def migrate_database():
    """Migrate the database to add missing columns"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run init_db.py first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        print("=" * 50)
        
        # Check if smtp_profile_id column exists in template table
        cursor.execute("PRAGMA table_info(template)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'smtp_profile_id' not in columns:
            print("📝 Adding smtp_profile_id column to template table...")
            cursor.execute("ALTER TABLE template ADD COLUMN smtp_profile_id INTEGER")
            print("✅ Added smtp_profile_id column")
            
            # Update existing templates to use the first SMTP profile
            print("🔄 Updating existing templates with default SMTP profile...")
            cursor.execute("SELECT id FROM smtp_profiles LIMIT 1")
            smtp_profile = cursor.fetchone()
            
            if smtp_profile:
                cursor.execute("UPDATE template SET smtp_profile_id = ?", (smtp_profile[0],))
                print(f"✅ Updated templates to use SMTP profile ID: {smtp_profile[0]}")
            else:
                print("⚠️  No SMTP profiles found. Please create one first.")
                cursor.execute("UPDATE template SET smtp_profile_id = 1")
                print("✅ Set default smtp_profile_id to 1")
        else:
            print("✅ smtp_profile_id column already exists")
        
        # Commit changes
        conn.commit()
        
        print("=" * 50)
        print("🎉 Database migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
