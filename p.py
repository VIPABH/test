from telethon import TelegramClient, events
import json, os

# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# تشغيل العميل
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# التحقق من وجود ملف JSON أو إنشائه
if not os.path.exists("users.json"):
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump([], file)

@ABH.on(events.NewMessage)
async def store_user_info(event):
    # التحقق من أن الرسالة من مستخدم وليس من قناة أو جروب
    if event.is_group or event.is_channel:
        return  # تجاهل الرسائل من القنوات والجروبات

    sender = await event.get_sender()  # جلب معلومات الشخص
    chat_id = event.chat_id  # ID المحادثة للرد على المستخدم

    if not sender:  # تأكد أن sender ليس None
        return

    # استخراج البيانات المهمة
    user_info = {
        "id": sender.id,
        "username": sender.username,
        "first_name": sender.first_name,
        "last_name": sender.last_name,
        "phone": sender.phone,
        "is_bot": sender.bot
    }

    # قراءة البيانات الحالية مع التعامل مع ملف JSON فارغ أو معطوب
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            users = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        users = []  # إذا كان الملف فارغًا أو غير موجود، يتم تعيين قائمة فارغة

    # تجنب تكرار تخزين نفس المستخدم باستخدام Set للتحقق بسرعة
    existing_user_ids = {u["id"] for u in users}
    
    if user_info["id"] not in existing_user_ids:
        users.append(user_info)

        # إعادة حفظ البيانات
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

        print(f"تم تخزين بيانات جديدة: {sender.first_name}")

    # **إرسال معلومات المستخدم عند كتابة "دز"**
    if event.raw_text.strip().lower() in ["دز", "دِزْ", "دَزْ"]:  # دعم عدة طرق للكتابة
        user_info_text = (
            f"👤 **معلومات المستخدم:**\n"
            f"🆔 ID: `{sender.id}`\n"
            f"📛 الاسم: {sender.first_name or 'لا يوجد'} {sender.last_name or ''}\n"
            f"🔹 اسم المستخدم: @{sender.username if sender.username else 'لا يوجد'}\n"
            f"📞 الهاتف: {sender.phone if sender.phone else 'غير متاح'}\n"
            f"🤖 بوت؟ {'نعم' if sender.bot else 'لا'}"
        )

        await ABH.send_message(chat_id, user_info_text)

    # **إرسال جميع المستخدمين عند كتابة "كل المستخدمين"**
    elif event.raw_text.strip().lower() == "كل المستخدمين":
        if not users:
            await ABH.send_message(chat_id, "⚠️ لا يوجد مستخدمون مخزنين بعد.")
            return

        all_users_text = "📜 **قائمة المستخدمين المسجلين:**\n\n"
        messages = []  # قائمة لتخزين الرسائل المقسمة
        for user in users:
            user_info_text = (
                f"🆔 ID: `{user['id']}`\n"
                f"📛 الاسم: {user['first_name'] or 'لا يوجد'} {user['last_name'] or ''}\n"
                f"🔹 اسم المستخدم: @{user['username'] if user['username'] else 'لا يوجد'}\n"
                f"📞 الهاتف: {user['phone'] if user['phone'] else 'غير متاح'}\n"
                f"🤖 بوت؟ {'نعم' if user['is_bot'] else 'لا'}\n"
                f"——————————————\n"
            )
            if len(all_users_text) + len(user_info_text) > 4000:
                messages.append(all_users_text)  # إضافة الجزء المكتمل إلى القائمة
                all_users_text = ""  # إعادة التهيئة

            all_users_text += user_info_text

        messages.append(all_users_text)  # إضافة الجزء الأخير إلى القائمة

        for msg in messages:
            await ABH.send_message(chat_id, msg)

    # **البحث عن مستخدم عبر الـ ID أو اسم المستخدم**
    elif event.raw_text.strip().lower().startswith("بحث "):
        query = event.raw_text.strip().split(" ", 1)[1]
        found_users = [
            user for user in users
            if query in str(user["id"]) or (user["username"] and query.lower() in user["username"].lower())
        ]

        if not found_users:
            await ABH.send_message(chat_id, f"❌ لم يتم العثور على أي مستخدم باسم أو ID: `{query}`")
            return

        search_result_text = "🔍 **نتائج البحث:**\n\n"
        for user in found_users:
            search_result_text += (
                f"🆔 ID: `{user['id']}`\n"
                f"📛 الاسم: {user['first_name'] or 'لا يوجد'} {user['last_name'] or ''}\n"
                f"🔹 اسم المستخدم: @{user['username'] if user['username'] else 'لا يوجد'}\n"
                f"📞 الهاتف: {user['phone'] if user['phone'] else 'غير متاح'}\n"
                f"🤖 بوت؟ {'نعم' if user['is_bot'] else 'لا'}\n"
                f"——————————————\n"
            )

        await ABH.send_message(chat_id, search_result_text)

# تشغيل البوت
ABH.run_until_disconnected()
