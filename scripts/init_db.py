import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine, Base
from app.models import CustomerAllowlist, SmtpProfile, Template

async def init_database():
    print("Initializing database...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully!")
        
        # Verify tables exist
        async with engine.begin() as conn:
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = result.fetchall()
            print(f"Available tables: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
