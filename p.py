from telethon import events
import json

@ABH.on(events.NewMessage)
async def store_user_info(event):
    sender = await event.get_sender()  # جلب معلومات الشخص

    # استخراج البيانات المهمة
    user_info = {
        "id": sender.id,
        "username": sender.username,
        "first_name": sender.first_name,
        "last_name": sender.last_name,
        "phone": sender.phone,
        "is_bot": sender.bot
    }

    # حفظ البيانات في ملف JSON
    with open("users.json", "a", encoding="utf-8") as file:
        json.dump(user_info, file, ensure_ascii=False, indent=4)
        file.write(",\n")  # فصل كل مستخدم بفاصلة

    print(f"تم حفظ بيانات المستخدم: {sender.first_name}")

ABH.run_until_disconnected()
