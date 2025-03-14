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
    sender = await event.get_sender()  # جلب معلومات الشخص
    chat_id = event.chat_id  # ID المحادثة للرد على المستخدم

    # استخراج البيانات المهمة
    user_info = {
        "id": sender.id,
        "username": sender.username,
        "first_name": sender.first_name,
        "last_name": sender.last_name,
        "phone": sender.phone,
        "is_bot": sender.bot
    }

    # قراءة البيانات الحالية
    with open("users.json", "r", encoding="utf-8") as file:
        users = json.load(file)

    # تجنب التكرار
    if not any(u["id"] == user_info["id"] for u in users):
        users.append(user_info)

        # إعادة حفظ البيانات
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

        print(f"تم تخزين بيانات جديدة: {sender.first_name}")

    # **عند إرسال كلمة "دز" يرسل معلومات المستخدم**
    if event.raw_text.strip() == "دز":
        user_info_text = (
            f"👤 **معلومات المستخدم:**\n"
            f"🆔 ID: `{sender.id}`\n"
            f"📛 الاسم: {sender.first_name or 'لا يوجد'} {sender.last_name or ''}\n"
            f"🔹 اسم المستخدم: @{sender.username if sender.username else 'لا يوجد'}\n"
            f"📞 الهاتف: {sender.phone if sender.phone else 'غير متاح'}\n"
            f"🤖 بوت؟ {'نعم' if sender.bot else 'لا'}"
        )

        await ABH.send_message(chat_id, user_info_text)

# تشغيل البوت
ABH.run_until_disconnected()
