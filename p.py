from telethon import TelegramClient, events
import os

SESSION = 'session'
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ABH = TelegramClient(SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
@ABH.on(events.NewMessage(pattern="^يوزري$"))
async def handler(event):
    s = await event.get_sender()
    u = s.username
    await event.reply(f"`@{u}` @{u}")
@ABH.on(events.NewMessage(pattern="^يوزره|يوزرة|اليوزر$"))
async def handler(event):
    r = event.get_reply_message()
    s = await r.get_sender()
    u = s.username
    await event.reply(f"`@{u}` @{u}")
ABH.run_until_disconnected()
