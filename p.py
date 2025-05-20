from telethon import TelegramClient, events
import os

SESSION = 'session'
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ABH = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@ABH.on(events.NewMessage)
async def handler(event):
    s = await event.get_sender()

    # تجهيز قائمة اليوزرات الإضافية
    usernames_list = []
    if hasattr(s, "usernames") and s.usernames:
        usernames_list = [u.username for u in s.usernames]

    # فحص إذا الرقم متوفر
    phone_text = f"{s.phone}" if hasattr(s, "phone") and s.phone else "🚫 غير متاح"

    await event.reply(
        f"اهلا {s.first_name or 'مستخدم'}\n"
        f"يوزرك: @{s.username}" if s.username else "يوزرك: None\n"
        f"رقمك: {phone_text}\n"
        f"يوزراتك الإضافية: {', '.join(usernames_list) if usernames_list else 'لا توجد'}"
    )

ABH.run_until_disconnected()
