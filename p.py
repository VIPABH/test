from telethon import TelegramClient, events
import os
from faker import Faker 
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
if not all([api_id, api_hash, bot_token]):
    raise ValueError("الرجاء ضبط المتغيرات البيئية API_ID, API_HASH, و BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
fake = Faker("ar_AA")
@ABH.on(events.NewMessage)
async def a(event):
    a = fake.word()
    await event.reply(f'{a}')

ABH.run_until_disconnected()
