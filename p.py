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
    us = {', '.join(usernames_list) if usernames_list else 'لا توجد'}
    usernames_list = []
    if hasattr(s, "usernames") and s.usernames:
        usernames_list = [u.username for u in s.usernames]
        n = {s.phone if hasattr(s, 'phone') and s.phone else '🚫 غير متاح'}
    main_username = s.username or (usernames_list[0] if usernames_list else None)
    u = f'@{main_username}' if main_username else '🚫 غير متاح'
    m = {s.first_name or 'مستخدم'}
    await event.reply(
f'''        اهلا {m}\n
        رقمك:{n}\n
        يوزرك: {u}\n
        يوزراتك الإضافية: {us}
'''    )


ABH.run_until_disconnected()
