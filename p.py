from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import os


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


@ABH.on(events.NewMessage(pattern=r'^id (.+)'))
async def handler(event):
    input_data = event.pattern_match.group(1).strip()

    try:
        # جلب معلومات المستخدم
        user = await ABH.get_entity(input_data)
        full_user = await ABH(GetFullUserRequest(user.id))
        user_info = full_user.user

        # استخراج المعلومات
        user_id = user_info.id
        username = f"@{user_info.username}" if user_info.username else "—"
        full_name = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
        phone = user_info.phone if user_info.phone else "—"

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
        await event.reply(f"⚠️ حدث خطأ: {e}")

print("🔄 Running...")
ABH.run_until_disconnected()
