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

# تنزيل الورود (فقط للشخص الذي رفعها أو الذي تم رفعها له)
@ABH.on(events.NewMessage(pattern=r'تنزيل وردة\s+(\d+)'))
async def remove_rose_handler(event):
    number = int(event.pattern_match.group(1))  
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لتنزيل الوردة!")
        return
    
    executor_id = str(event.sender_id)  # الشخص الذي يريد تنزيل الورود
    target_id = str(message.sender_id)  # الشخص الذي سيتم تنزيل الورود منه
    gid = str(event.chat_id)

    add_user(target_id, gid, message.sender.first_name, rose)

    if "giver" not in rose[gid][target_id]:
        await event.reply("❌ لا توجد معلومات عن الشخص الذي رفع هذه الورود!")
        return

    giver_id = rose[gid][target_id]["giver"]  # الشخص الذي رفع الورود لهذا المستخدم

    # التحقق من أن الذي ينزل الورود هو نفسه الذي رفعها أو المستخدم نفسه
    if executor_id != target_id and executor_id != giver_id:
        await event.reply("❌ لا يمكنك تنزيل هذه الورود، فقط الشخص الذي رفعها أو الذي تم رفعها له يمكنه ذلك!")
        return

    current_roses = rose[gid][target_id]["roses"]  

    if current_roses >= number:
        rose[gid][target_id]["roses"] -= number
        save_data(rose)
        await event.reply(f"✅ تم تنزيل {number} وردة من {message.sender.first_name} 🌹!")
    else:
        await event.reply(f"❌ لا يمكنك تنزيل {number} وردة، لديه فقط {current_roses} وردة!")

# عرض الفلوس والورود في المجموعة
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

# تشغيل البوت
ABH.run_until_disconnected()
