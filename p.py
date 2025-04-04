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
        rose[gid][uid] = {"name": nid, "money": 100, "roses": 0, "giver": None}  # تخزين معرّف الشخص الذي رفع الورود
    save_data(rose)

# شراء الورود وتسجيل المشتري
@ABH.on(events.NewMessage(pattern=r'رفع وردة\s+(\d+)'))
async def rose_handler(event):
    number = int(event.pattern_match.group(1))  
    message = await event.get_reply_message()
    
    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لرفع الوردة!")
        return
    
    giver_id = str(event.sender_id)  # الشخص الذي قام بالرفع
    receiver_id = str(message.sender_id)  # الشخص الذي تم رفع الورود له
    receiver_name = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    add_user(receiver_id, gid, receiver_name, rose)

    current_money = rose[gid][giver_id]["money"]
    cost_per_rose = 2  
    total_cost = number * cost_per_rose  

    if current_money >= total_cost:
        # خصم الفلوس من المشتري وزيادة الورود للمتلقي
        rose[gid][giver_id]["money"] -= total_cost
        rose[gid][receiver_id]["roses"] += number
        rose[gid][receiver_id]["giver"] = giver_id  # تسجيل الشخص الذي أعطى الورود
        save_data(rose)
        await event.reply(f"✅ تم شراء {number} وردة لـ {receiver_name} 🌹 بخصم {total_cost} فلوس!")
    else:
        await event.reply(f"❌ لا يمكنك شراء {number} وردة، تحتاج إلى {total_cost} فلوس ولكن لديك فقط {current_money} فلوس!")
@ABH.on(events.NewMessage(pattern=r'تنزيل وردة\s+(\d+)'))
async def remove_rose_handler(event):
    number = int(event.pattern_match.group(1))  
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لتنزيل الوردة!")
        return
    
    executor_id = str(event.sender_id)  # الشخص الذي يريد التنزيل
    target_id = str(message.sender_id)  # الشخص الذي سيتم تنزيل الورود منه
    gid = str(event.chat_id)

    add_user(target_id, gid, message.sender.first_name, rose)
    add_user(executor_id, gid, event.sender.first_name, rose)  # ضمان وجود المنفّذ في البيانات

    if "giver" not in rose[gid][target_id]:
        await event.reply("❌ لا توجد معلومات عن الشخص الذي رفع هذه الورود!")
        return

    giver_id = rose[gid][target_id]["giver"]  # الشخص الذي رفع الورود

    # تحديد سعر التنزيل
    if executor_id == target_id or executor_id == giver_id:
        price_per_rose = 2
    else:
        price_per_rose = 4

    total_roses_to_remove = number * price_per_rose
    current_roses = rose[gid][target_id]["roses"]

    if current_roses >= total_roses_to_remove:
        rose[gid][target_id]["roses"] -= total_roses_to_remove
        save_data(rose)
        await event.reply(
            f"✅ تم تنزيل {total_roses_to_remove} وردة من {message.sender.first_name} 🌹 حسب سعر {price_per_rose} لكل وردة!"
        )
    else:
        await event.reply(
            f"❌ لا يمكنك تنزيل {total_roses_to_remove} وردة، لديه فقط {current_roses} وردة!"
        )

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
