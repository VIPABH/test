from telethon import TelegramClient, events
import os

api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.NewMessage(pattern=r'id'))
async def handler(event):
    if event.is_reply:
        replied_message = await event.get_reply_message()
        sender_id = replied_message.sender_id
    else:
        sender_id = event.sender_id
        user = await ABH.get_entity(sender_id)        
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name if user.last_name else ''
        full_name = f"{first_name} {last_name}".strip()
        phone = user.phone if hasattr(user, 'phone') else "None"
        premium = "نعم" if user.premium else "لا"
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["—"]
        usernames_list = " ".join(usernames)  
        if user.photo:
            photo = await ABH.download_profile_photo(user.id)
        else:
            photo = None
        if photo:
            await event.respond(f"{user_id}\n{first_name}\n{premium}\n{full_name}\n{phone}\n {usernames_list}", file="photo")
        else:
            await event.respond('result')

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
from telethon import TelegramClient, events
import os

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# مجلد الصور المحلية
LOCAL_PHOTO_DIR = "photos"
os.makedirs(LOCAL_PHOTO_DIR, exist_ok=True)

@ABH.on(events.NewMessage(pattern=r'id', forwards=False))
async def handler(event):
    try:
        # التحقق إذا كان الرد على رسالة
        if event.is_reply:
            replied_message = await event.get_reply_message()
            sender_id = replied_message.sender_id
        else:
            sender_id = event.sender_id
        
        user = await ABH.get_entity(sender_id)
        
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name if user.last_name else ''
        full_name = f"{first_name} {last_name}".strip()
        phone = user.phone if hasattr(user, 'phone') else "—"
        premium = "نعم" if user.premium else "لا"
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["—"]
        usernames_list = " ".join(usernames)

        message_text = (
            f"🆔 **ID**: `{user_id}`\n"
            f"👤 **الاسم**: {full_name or '—'}\n"
            f"📞 **رقم الهاتف**: {phone}\n"
            f"💎 **اشتراك مميز**: {premium}\n"
            f"🔗 **أسماء المستخدمين**: {usernames_list}"
        )

        if user.photo:
            # اسم الملف المحلي
            photo_path = os.path.join(LOCAL_PHOTO_DIR, f"{user_id}.jpg")

            # تحميل الصورة في الملف المحلي
            await ABH.download_profile_photo(user.id, file=photo_path)

            # إرسال الصورة
            await ABH.send_file(
                event.chat_id,
                photo_path,
                caption=message_text,
                force_document=False  # إرسال كصورة
            )
        else:
            await event.respond(message_text)
    
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
