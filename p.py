import os
from telethon import TelegramClient, events

# قراءة القيم من متغيرات البيئة
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تعريف العميل (Client)
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# معرف المستخدم المستهدف الذي سيتم حذف رسائله
TARGET_USER_ID = 1421907917
pending_deletions_count = 0

# أمر التفعيل - يمكن لأي شخص استخدامه
@bot.on(events.NewMessage(pattern=r'^/حذف القادم$'))
async def trigger_deletion(event):
    global pending_deletions_count
    pending_deletions_count = 2
    await event.reply("سيتم حذف أول رسالتين قادمتين من المستخدم المحدد.")

# الحذف التلقائي عند استلام رسالة من الشخص المستهدف
@bot.on(events.NewMessage)
async def delete_target_messages(event):
    global pending_deletions_count
    if event.sender_id == TARGET_USER_ID and pending_deletions_count > 0:
        await event.delete()
        pending_deletions_count -= 1

# تشغيل البوت
bot.run_until_disconnected()
