import os
import time
from telethon import TelegramClient, events
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.NewMessage(pattern='^(حظر|.حظر|حظر$|/حظر)(.*)'))
async def send_message(event):
    p = event.pattern_match.group(2)
    if p:
        await event.reply(f'**جاري حظر {p}**')
    else:
        await event.reply('**يرجى تحديد المستخدم الذي تريد حظره.**')
        return
ABH.run_until_disconnected()
