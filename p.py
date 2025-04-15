from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
import os

# إعداد بيانات الاتصال
api_id = int(os.getenv('API_ID', '123456'))  # ضع API_ID الخاص بك هنا إن لم تستخدم متغيرات بيئة
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern=r'^id$'))
async def handler(event):
    try:
        sender = await event.get_sender()
        
        # جلب المعلومات التفصيلية عن المرسل
        user_full = await bot(GetFullUserRequest(sender.id))
        
        # استخراج معلومات المستخدم من الكائن الكامل
        user = user_full.users[0] if hasattr(user_full, 'users') and user_full.users else sender

        # عرض البيانات
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        phone = user.phone if user.phone else "—"

        result = (
            f"🆔 ID: `{user_id}`\n"
            f"👤 الاسم: {full_name or '—'}\n"
            f"🔗 يوزر: {username}\n"
            f"📞 رقم الهاتف: {phone}"
        )

        await event.reply(result)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء استخراج المعلومات:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
bot.run_until_disconnected()
