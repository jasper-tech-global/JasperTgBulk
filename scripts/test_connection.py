import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from aiogram import Bot
from app.core.config import settings

async def test_connection():
    try:
        print(f'Token loaded: {bool(settings.telegram_bot_token)}')
        print(f'Token prefix: {settings.telegram_bot_token[:12]}...')
        
        bot = Bot(token=settings.telegram_bot_token)
        print('Testing connection to api.telegram.org...')
        
        me = await bot.get_me()
        print(f'SUCCESS! Bot connected: @{me.username} (ID: {me.id})')
        
        await bot.session.close()
        return True
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if result:
        print('\nConnection test PASSED - Bot should work!')
    else:
        print('\nConnection test FAILED - Check network/firewall settings')
    
    input('\nPress Enter to continue...')
