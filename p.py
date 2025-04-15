from telethon import TelegramClient, events
import os

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
            # استخراج بيانات المرسل في الرسالة المستجيبة (التي يتم الرد عليها)
            replied_message = await event.get_reply_message()
            sender_id = replied_message.sender_id
        else:
            # إذا كانت الرسالة مباشرة من المستخدم
            sender_id = event.sender_id
        
        # استخراج بيانات المرسل
        user = await ABH.get_entity(sender_id)
        
        # استخراج المعلومات المطلوبة
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name if user.last_name else ''
        full_name = f"{first_name} {last_name}".strip()  # الاسم الكامل
        phone = user.phone if hasattr(user, 'phone') else "—"  # رقم الهاتف (إذا كان متاحًا)
        premium = "نعم" if user.premium else "لا"  # حالة الاشتراك المميز
        
        # جلب جميع أسماء المستخدمين المرتبطة بالحساب (إذا كانت موجودة)
        usernames = [f"@{username.username}" for username in user.usernames] if user.usernames else ["—"]
        usernames_list = " ".join(usernames)  # عرض جميع أسماء المستخدمين في سطر واحد

        # تحميل الصورة الشخصية (إذا كانت موجودة)
        if user.photo:
            photo = await ABH.download_profile_photo(user.id)  # تحميل الصورة كملف مؤقت
        else:
            photo = None

        # بناء الرسالة
        result = (
            f"🆔 **ID**: `{user_id}`\n"
            f"👤 **الاسم**: {full_name or '—'}\n"
            f"📞 **رقم الهاتف**: {phone}\n"
            f"💎 **اشتراك مميز**: {premium}\n"
            f"🔗 **أسماء المستخدمين**: {usernames_list}\n"
        )

        # إرسال الرسالة مع الصورة الشخصية إذا كانت موجودة
        if photo:
            await event.respond(result, file=photo)  # إرسال النص مع الصورة في نفس الرسالة
        else:
            await event.respond(result)
    
    except Exception as e:
        # التعامل مع الأخطاء
        await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
