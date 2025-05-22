from telethon import TelegramClient, events, Button
from Resources import mention #type: ignore
import asyncio, os, random, uuid
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.ChatAction)
async def handler(event):
    await event.reply(str(event))
ABH.run_until_disconnected()
