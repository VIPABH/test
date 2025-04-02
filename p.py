import os
import json
from telethon import TelegramClient, events

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل النقاط من ملف JSON
def load_points(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ النقاط إلى ملف JSON
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

rose = load_points()

# إضافة أو تحديث نقاط الورود
def add_points(uid, gid, nid, rose):
    uid, gid = str(uid), str(gid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "count": 40}  # بداية الترصيد الافتراضي
    save_points(rose)

@ABH.on(events.NewMessage(pattern=r'رفع وردة\s+(\d+)'))
async def rose_handler(event):
    number = int(event.pattern_match.group(1))  # استخراج العدد المطلوب
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("🚫 يجب الرد على رسالة شخص لرفع الوردة!")
        return

    uid = str(message.sender_id)
    nid = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    # التأكد من أن الشخص موجود وإضافة بياناته إذا لم يكن كذلك
    add_points(uid, gid, nid, rose)

    # التحقق من الرصيد
    if rose[gid][uid]["count"] >= number:
        rose[gid][uid]["count"] -= number  # خصم الورود
        save_points(rose)
        await event.reply(f"✅ تم رفع {number} وردة لـ {nid} 🌹")
    else:
        await event.reply("🚫 يا فقير، ما عندك ورد كافي!")

@ABH.on(events.NewMessage(pattern='الورود'))
async def show_handler(event):
    chat_id = str(event.chat_id)

    if chat_id not in rose or not rose[chat_id]:
        await event.reply("🚫 لا يوجد أي ورود في هذه المجموعة حتى الآن.")
        return

    response = "🌹 قائمة الورود في هذه المجموعة:\n"
    for uid, data in rose[chat_id].items():
        response += f"👤 {data['name']}: {data['count']} وردة\n"

    await event.reply(response)

ABH.run_until_disconnected()
