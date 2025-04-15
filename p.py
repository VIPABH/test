import os
from telethon import TelegramClient, events

# قراءة القيم من متغيرات البيئة
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تشغيل العميل
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# المعالج لحذف الرسائل التي تحتوي على "مالي خلقك"
@bot.on(events.NewMessage(pattern="مالي خلقك"))
async def delete_target_messages(event):
    await event.delete()

# تشغيل البوت حتى يتم إيقافه
bot.run_until_disconnected()
