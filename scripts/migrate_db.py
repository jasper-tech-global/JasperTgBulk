#!/usr/bin/env python3
"""
Database Migration Script for Jasper TG BULK
Removes smtp_profile_id column from templates table and adds active column to smtp_profiles table
"""

import sqlite3
import os
import sys

def migrate_database():
    """Migrate the database to the new schema"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting database migration...")
        
        # Check if smtp_profile_id column exists in templates table
        cursor.execute("PRAGMA table_info(template)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'smtp_profile_id' in columns:
            print("Removing smtp_profile_id column from templates table...")
            
            # Create new table without smtp_profile_id
            cursor.execute("""
                CREATE TABLE template_new (
                    id INTEGER PRIMARY KEY,
                    code VARCHAR(64) NOT NULL,
                    subject_template VARCHAR(500) NOT NULL,
                    body_template TEXT NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code)
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO template_new (id, code, subject_template, body_template, active, created_at)
                SELECT id, code, subject_template, body_template, 1, created_at FROM template
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE template")
            cursor.execute("ALTER TABLE template_new RENAME TO template")
            
            print("✅ Successfully removed smtp_profile_id column from templates table")
        else:
            print("✅ smtp_profile_id column already removed from templates table")
        
        # Check if active column exists in smtp_profiles table
        cursor.execute("PRAGMA table_info(smtp_profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'active' not in columns:
            print("Adding active column to smtp_profiles table...")
            cursor.execute("ALTER TABLE smtp_profiles ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1")
            print("✅ Successfully added active column to smtp_profiles table")
        else:
            print("✅ active column already exists in smtp_profiles table")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
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
