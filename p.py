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

    # استخراج الاسم
    m = s.first_name or 'مستخدم'

    # استخراج الرقم إن توفر
    n = s.phone if hasattr(s, 'phone') and s.phone else '🚫 غير متاح'

    # استخراج اليوزرات الإضافية
    usernames_list = [u.username for u in s.usernames] if hasattr(s, "usernames") and s.usernames else []
    us = ', '.join([f"@{u}" for u in usernames_list]) if usernames_list else 'لا توجد'

    # تحديد اليوزر الرئيسي
    main_username = s.username or (usernames_list[0] if usernames_list else None)
    u = f'@{main_username}' if main_username else '🚫 غير متاح'

    # الرد النهائي
    await event.reply(
f'''اهلا {m}
رقمك: {n}
يوزرك: {u}
يوزراتك الإضافية: {us}'''
    )

ABH.run_until_disconnected()
