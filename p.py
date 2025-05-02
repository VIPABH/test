from telethon import TelegramClient, events
import re
import asyncio
import os

# إعدادات API
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('s', api_id, api_hash)

@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.is_reply))
async def handle_reply_to_self(event):
    replied = await event.get_reply_message()
    if replied and replied.sender_id == (await ABH.get_me()).id:
        await event.respond("رديت على رسالتي حتى لو ما ذكرتني 👍")

async def main():
    await ABH.start()
    await ABH.run_until_disconnected()

asyncio.run(main())
