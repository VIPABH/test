from telethon import TelegramClient, events
import re
import asyncio
import os

# إعدادات API
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('s', api_id, api_hash)
@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.is_reply and e.mentioned))
async def handle_reply(event):
    replied_msg = await event.get_reply_message()
    await event.respond(f"رديت على: {replied_msg.text}")
async def main():
    await ABH.start()
    await ABH.run_until_disconnected()

asyncio.run(main())
