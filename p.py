from telethon import TelegramClient, events
import os
import tempfile

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

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
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                await ABH.download_profile_photo(user.id, file=tmp_file.name)
                tmp_file_path = tmp_file.name
            
            # إرسال الصورة كـ صورة حقيقية باستخدام send_file
            await ABH.send_file(
                event.chat_id,
                tmp_file_path,
                caption=message_text,
                force_document=False  # هذا يضمن إرسال الصورة كصورة وليس ملف
            )

            os.remove(tmp_file_path)
        else:
            await event.respond(message_text)
    
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
