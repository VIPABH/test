from telethon import TelegramClient, events
import asyncio, os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('code', api_id, api_hash)

@ABH.on(events.NewMessage(outgoing=True))
async def handle_outgoing(event):
    await event.reply('Hello, this is a test message!')

@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_private(event):
    await event.reply('Hello!')

ABH.start()
ABH.run_until_disconnected()
