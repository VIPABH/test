from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import os

# تحميل القيم من متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))  # تأكد أنه رقم
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'^id (.+)'))
async def handler(event):
    input_data = event.pattern_match.group(1).strip()

    try:
        # جلب معلومات المستخدم
        user = await ABH.get_entity(input_data)
        full = await ABH(GetFullUserRequest(user.id))

        # استخدام الكائن مباشرة
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        phone = user.phone if user.phone else "—"

        # إرسال النتائج
        result = (
            f"🆔 ID: `{user_id}`\n"
            f"👤 الاسم: {full_name or '—'}\n"
            f"🔗 يوزر: {username}\n"
            f"📞 رقم الهاتف: {phone}"
        )
        await event.reply(result)

    except (UsernameNotOccupiedError, UsernameInvalidError):
        await event.reply("❌ هذا اليوزر غير موجود.")
    except ValueError:
        await event.reply("❌ المعرف غير صالح.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
