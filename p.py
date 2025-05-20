from telethon import TelegramClient, events
import os

SESSION = 'session'
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ABH = TelegramClient(SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@ABH.on(events.NewMessage)
async def handler(event):
    s = await event.get_sender()

    # استخراج قائمة اليوزرات الإضافية (إن وجدت)
    usernames_list = []
    if hasattr(s, "usernames") and s.usernames:
        usernames_list = [u.username for u in s.usernames]

    # تحديد اليوزر الأساسي: إما s.username أو أول يوزر من قائمة usernames
    main_username = s.username or (usernames_list[0] if usernames_list else None)

    # إعداد النص النهائي
    await event.reply(
        f"اهلا {s.first_name or 'مستخدم'}\n"
        f"يوزرك: @{main_username}" if main_username else "يوزرك: None\n"
        f"رقمك: {s.phone if hasattr(s, 'phone') and s.phone else '🚫 غير متاح'}\n"
        f"يوزراتك الإضافية: {', '.join(usernames_list) if usernames_list else 'لا توجد'}"
    )

ABH.run_until_disconnected()
