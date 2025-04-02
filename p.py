import os
import json
from telethon import TelegramClient, events

# تحميل متغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تشغيل البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل بيانات الورود والفلوس من ملف JSON
def load_points(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ بيانات الورود والفلوس
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل البيانات
rose = load_points()

# إضافة مستخدم جديد مع فلوس وافتراضيًا 40 وردة
def add_points(uid, gid, nid, rose):
    uid, gid = str(uid), str(gid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "count": 40, "money": 100}  # يبدأ المستخدم بـ 100 فلوس
    save_points(rose)

# رفع الورود مع خصم الفلوس عند الحاجة
@ABH.on(events.NewMessage(pattern=r'رفع وردة\s+(\d+)'))
async def rose_handler(event):
    number = int(event.pattern_match.group(1))  # عدد الورود المطلوبة
    message = await event.get_reply_message()
    
    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لرفع الوردة!")
        return
    
    uid = str(message.sender_id)
    nid = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    # إضافة المستخدم إذا لم يكن موجودًا
    add_points(uid, gid, nid, rose)

    current_roses = rose[gid][uid]["count"]  # عدد الورود الحالي
    current_money = rose[gid][uid]["money"]  # الرصيد الحالي

    if current_roses >= number:
        # إذا كان لديه ورود كافية، يتم خصم العدد مباشرة
        rose[gid][uid]["count"] -= number
        save_points(rose)
        await event.reply(f"✅ تم رفع {number} وردة لـ {nid} 🌹")
    
    elif current_roses + current_money >= number:
        # إذا كان لديه ورود غير كافية لكن يستطيع الشراء من رصيده
        needed_roses = number - current_roses
        cost = needed_roses  # كل وردة = 1 فلوس

        rose[gid][uid]["count"] = 0  # ينتهي رصيد الورود
        rose[gid][uid]["money"] -= cost  # خصم الفلوس
        save_points(rose)

        await event.reply(f"⚠️ كان عند {nid} {current_roses} وردة فقط، تم استخدامها واشترى {needed_roses} وردة بخصم {cost} فلوس! 💰")
    
    else:
        # إذا لم يكن لديه ورود ولا فلوس كافية
        await event.reply(f"❌ لا يمكنك رفع {number} وردة، ليس لديك ورود كافية ولا فلوس كافية!")

# عرض الورود والفلوس في المجموعة
@ABH.on(events.NewMessage(pattern='الورود'))
async def show_handler(event):
    chat_id = str(event.chat_id)

    if chat_id not in rose or not rose[chat_id]:
        await event.reply("❌ لا يوجد أي ورود في هذه المجموعة حتى الآن.")
        return

    response = "🌹 قائمة الورود والفلوس في هذه المجموعة:\n"
    for uid, data in rose[chat_id].items():
        response += f"👤 {data['name']}: {data['count']} وردة | 💰 {data['money']} فلوس\n"

    await event.reply(response)

# تشغيل البوت
ABH.run_until_disconnected()
