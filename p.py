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
def add_user(uid, gid, nid, rose):
    uid, gid = str(uid), str(gid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "money": 1200, "roses": 0, "giver": None}  # تخزين معرّف الشخص الذي رفع الورود
    save_data(rose)

@ABH.on(events.NewMessage(pattern=r'رفع وردة'))
async def promote_handler(event):
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لرفع الوردة!")
        return

    giver_id = str(event.sender_id)
    receiver_id = str(message.sender_id)
    receiver_name = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    add_user(receiver_id, gid, receiver_name, rose)
    add_user(giver_id, gid, event.sender.first_name, rose)

    if rose[gid][receiver_id].get("status") == "مرفوع":
        await event.reply("⚠️ هذا الشخص مرفوع بالفعل!")
        return

    cost = 2
    min_required = 1000
    current_money = rose[gid][giver_id]["money"]

    if current_money < min_required:
        await event.reply(f"❌ الحد الأدنى لتنفيذ أمر الرفع هو {min_required} فلوس، لديك فقط {current_money} فلوس.")
        return

    rose[gid][giver_id]["money"] -= cost
    rose[gid][receiver_id]["status"] = "مرفوع"
    rose[gid][receiver_id]["giver"] = giver_id
    save_data(rose)
    await event.reply(f"✅ تم رفع {receiver_name} إلى منصب 🌹 'مرفوع' مقابل {cost} فلوس.")
@ABH.on(events.NewMessage(pattern=r'تنزيل وردة'))
async def demote_handler(event):
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لتنزيل الوردة!")
        return

    executor_id = str(event.sender_id)
    target_id = str(message.sender_id)
    gid = str(event.chat_id)

    add_user(target_id, gid, message.sender.first_name, rose)
    add_user(executor_id, gid, event.sender.first_name, rose)

    if rose[gid][target_id].get("status") != "مرفوع":
        await event.reply("⚠️ هذا المستخدم ليس في منصب 'مرفوع'!")
        return

    giver_id = rose[gid][target_id].get("giver")
    if executor_id == target_id or executor_id == giver_id:
        cost = 2
    else:
        cost = 4

    min_required = 1000
    current_money = rose[gid][executor_id]["money"]

    if current_money < min_required:
        await event.reply(f"❌ الحد الأدنى لتنفيذ أمر التنزيل هو {min_required} فلوس، لديك فقط {current_money} فلوس.")
        return

    rose[gid][executor_id]["money"] -= cost
    rose[gid][target_id]["status"] = "عادي"
    rose[gid][target_id]["giver"] = None
    save_data(rose)
    await event.reply(f"✅ تم تنزيل {message.sender.first_name} من منصب 'مرفوع' مقابل {cost} فلوس.")

@ABH.on(events.NewMessage(pattern='الحساب'))
async def show_handler(event):
    chat_id = str(event.chat_id)

    if chat_id not in rose or not rose[chat_id]:
        await event.reply("❌ لا يوجد أي بيانات مالية في هذه المجموعة حتى الآن.")
        return

    response = "💰 قائمة الحسابات في هذه المجموعة:\n"
    for uid, data in rose[chat_id].items():
        response += f"👤 {data['name']}: 💰 {data['money']} فلوس | 🌹 {data['roses']} ورود\n"

    await event.reply(response)

ABH.run_until_disconnected()
