from telethon import TelegramClient, events
import re
import asyncio
import os

# إعدادات API
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash)
@ABH.on(events.NewMessage(outgoing=True))
async def pin(event):
    await event.reply('Hello, this is a test message!')
@ABH.on(events.NewMessage(func=lambda e: e.is_private, incoming=True))
async def pin(event):
    await event.reply('Hello, !')

ABH.start()
