import os
from telethon import TelegramClient, events

# قراءة القيم من متغيرات البيئة
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تشغيل العميل
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# معرف المستخدم أو البوت المستهدف
TARGET_USER_ID = 1421907917

@bot.on(events.NewMessage(pattren="مالي خلقك"))
async def delete_target_messages(event):
    await event.delete()
bot.run_until_disconnected()
