from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
from telethon.tl.types import MessageMediaPhoto
import os

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'^id (.+)'))
async def handler(event):
    input_data = event.pattern_match.group(1).strip()

    try:
        # جلب معلومات المستخدم
        user = await ABH.get_entity(input_data)
        full_user = await ABH(GetFullUserRequest(user.id))
        user_info = full_user.user

        # البيانات الأساسية
        user_id = user_info.id
        username = f"@{user_info.username}" if user_info.username else "—"
        full_name = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
        phone = user_info.phone if user_info.phone else "—"
        bio = full_user.about if full_user.about else "—"

        # إنشاء رابط دائم (إن وجد يوزر)
        permalink = f"https://t.me/{user_info.username}" if user_info.username else "—"

        # إعداد الرسالة
        result = (
            f"🆔 ID: `{user_id}`\n"
            f"👤 الاسم: {full_name or '—'}\n"
            f"🔗 يوزر: {username}\n"
            f"📞 رقم الهاتف: {phone}\n"
            f"📝 نبذة: {bio}\n"
            f"🌐 رابط دائم: {permalink}"
        )

        # إرسال صورة البروفايل إن وُجدت
        if user_info.photo:
            photo = await ABH.download_profile_photo(user_info.id)
            await event.reply(result, file=photo)
            os.remove(photo)  # حذف الصورة بعد الإرسال للحفاظ على النظافة
        else:
            await event.reply(result)

    except (UsernameNotOccupiedError, UsernameInvalidError):
        await event.reply("❌ هذا اليوزر غير موجود.")
    except ValueError:
        await event.reply("❌ المعرف غير صالح.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
