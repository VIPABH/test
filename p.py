import os
import json
from telethon import TelegramClient, events

# تحميل متغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تشغيل البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل البيانات المالية
def load_data(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ البيانات المالية
def save_data(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل البيانات
rose = load_data()

# إضافة مستخدم جديد
def add_user(uid, gid, name, rose):
    uid, gid = str(uid), str(gid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {
            "name": name,
            "money": 1200,
            "status": "عادي",
            "giver": None
        }
    save_data(rose)

# أمر رفع الوردة (ترقية)
@ABH.on(events.NewMessage(pattern=r'رفع وردة'))
async def promote_handler(event):
    message = await event.get_reply_message()
    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة الشخص المراد رفعه.")
        return

    giver_id = str(event.sender_id)
    receiver_id = str(message.sender_id)
    receiver_name = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    add_user(receiver_id, gid, receiver_name, rose)
    add_user(giver_id, gid, event.sender.first_name, rose)

    if rose[gid][receiver_id]["status"] == "مرفوع":
        await event.reply("⚠️ هذا الشخص مرفوع بالفعل.")
        return

    min_required = 3000
    cost = min_required
    giver_money = rose[gid][giver_id]["money"]

    if giver_money < min_required:
        await event.reply(f"❌ الحد الأدنى للرفع هو {min_required} فلوس. رصيدك الحالي: {giver_money}.")
        return

    rose[gid][giver_id]["money"] -= cost
    rose[gid][receiver_id]["status"] = "مرفوع"
    rose[gid][receiver_id]["giver"] = giver_id
    save_data(rose)

    await event.reply(f"✅ تم رفع {receiver_name} إلى منصب 🌹 'مرفوع' مقابل {cost} فلوس.")

# أمر تنزيل الوردة (إلغاء الترقية)
@ABH.on(events.NewMessage(pattern=r'تنزيل وردة'))
async def demote_handler(event):
    message = await event.get_reply_message()
    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة الشخص المراد تنزيله.")
        return

    executor_id = str(event.sender_id)
    target_id = str(message.sender_id)
    target_name = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    add_user(target_id, gid, target_name, rose)
    add_user(executor_id, gid, event.sender.first_name, rose)

    if rose[gid][target_id]["status"] != "مرفوع":
        await event.reply("⚠️ هذا المستخدم ليس مرفوعًا.")
        return

    giver_id = rose[gid][target_id].get("giver")
    if executor_id == target_id or executor_id == giver_id:
        cost = 2
    else:
        cost = 4

    min_required = 3000
    executor_money = rose[gid][executor_id]["money"]

    if executor_money < min_required:
        await event.reply(f"❌ الحد الأدنى للتنزيل هو {min_required} فلوس. رصيدك الحالي: {executor_money}.")
        return

    rose[gid][executor_id]["money"] -= cost
    rose[gid][target_id]["status"] = "عادي"
    rose[gid][target_id]["giver"] = None
    save_data(rose)

    await event.reply(f"✅ تم تنزيل {target_name} من منصب 'مرفوع' مقابل {cost} فلوس.")

# عرض الحسابات
@ABH.on(events.NewMessage(pattern='الحساب'))
async def show_handler(event):
    chat_id = str(event.chat_id)
    if chat_id not in rose or not rose[chat_id]:
        await event.reply("❌ لا توجد بيانات مالية في هذه المجموعة.")
        return

    response = "📊 قائمة الحسابات:\n"
    for uid, data in rose[chat_id].items():
        status_icon = "🌹" if data["status"] == "مرفوع" else "👤"
        response += f"{status_icon} {data['name']}: 💰 {data['money']} فلوس | 🏷️ الحالة: {data['status']}\n"

    await event.reply(response)

# تشغيل البوت
ABH.run_until_disconnected()
