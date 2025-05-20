from telethon import TelegramClient, events
import random, os
SESSION = 'session'
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ABH = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
@ABH.on(events.NewMessage)
async def handler(event):
    s = await event.get_sender()
    await event.reply(f'اهلا {s.first_name} \n يوزرك {s.username}\n رقمك {s.phone}\n يوزراتك {s.usernames}')
ABH.run_until_disconnected()
