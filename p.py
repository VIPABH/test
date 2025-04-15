import os
from telethon import TelegramClient, events

# قراءة القيم من متغيرات البيئة
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تعريف العميل (Client)
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# تعريف الثوابت والحالة
TARGET_USER_ID = 1421907917
pending_deletions_count = 0
ison = False

@bot.on(events.NewMessage(pattern=r'^ح$'))
async def trigger_deletion(event):
    global pending_deletions_count, ison
    pending_deletions_count = 2
    ison = True
    await event.reply("سيتم حذف أول رسالتين قادمتين من المستخدم المحدد.")

@bot.on(events.NewMessage)
async def delete_target_messages(event):
    global pending_deletions_count, ison

    if ison and event.sender_id == TARGET_USER_ID and pending_deletions_count > 0:
        await event.delete()
        pending_deletions_count -= 1

        if pending_deletions_count == 0:
            ison = False  # إيقاف الحالة بعد حذف رسالتين

# تشغيل البوت
bot.run_until_disconnected()
