from telethon import TelegramClient, events
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import os

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'id'))
async def handler(event):
    try:
        sender_id = event.sender_id
        user = await ABH.get_entity(sender_id)

        # استخراج البيانات للمستخدم
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        phone = user.phone if hasattr(user, 'phone') and user.phone else "—"
        bio = user.bio if hasattr(user, 'bio') and user.bio else "—"
        
        # الرد على المرسل بمعلوماته
        result = (
            f"🆔 ID: `{user_id}`\n"
            f"👤 الاسم: {full_name or '—'}\n"
            f"🔗 يوزر: {username}\n"
            f"📞 رقم الهاتف: {phone}\n"
            f"📝 نبذة: {bio}\n"
        )
        await event.reply(result)
    
    except Exception as e:
        # التعامل مع الأخطاء
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
