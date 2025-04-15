from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
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
        full_user = await ABH(GetFullUserRequest(user.id))  # للحصول على النبذة

        # البيانات الأساسية من كائن user (وليس من full_user.user)
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        phone = user.phone if hasattr(user, 'phone') and user.phone else "—"
        bio = full_user.about if hasattr(full_user, 'about') and full_user.about else "—"
        permalink = f"https://t.me/{user.username}" if user.username else "—"

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
        if user.photo:
            photo = await ABH.download_profile_photo(user.id)
            await event.reply(result, file=photo)
            os.remove(photo)  # حذف الصورة بعد الإرسال
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
