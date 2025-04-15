from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
import os

# جلب بيانات API من متغيرات البيئة
api_id = int(os.getenv('API_ID'))  # تأكد أن هذا رقم صحيح
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء جلسة البوت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern=r'^id$'))
async def handler(event):
    try:
        sender = await event.get_sender()
        full_user = await bot(GetFullUserRequest(sender.id))
        user_info = full_user.user

        # استخراج المعلومات
        user_id = user_info.id
        username = f"@{user_info.username}" if user_info.username else "—"
        full_name = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
        phone = user_info.phone if user_info.phone else "—"

        # بناء الرسالة
        result = (
            f"🆔 ID: `{user_id}`\n"
            f"👤 الاسم: {full_name or '—'}\n"
            f"🔗 يوزر: {username}\n"
            f"📞 رقم الهاتف: {phone}"
        )
        await event.reply(result)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ: {e}")

print("🤖 البوت يعمل بنجاح...")
bot.run_until_disconnected()
