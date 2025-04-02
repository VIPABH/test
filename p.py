import os
import json
from telethon import TelegramClient, events

# تحميل متغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تشغيل البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل بيانات الفلوس من ملف JSON
def load_data(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ بيانات الفلوس
def save_data(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل البيانات
rose = load_data()

# إضافة مستخدم جديد مع 100 فلوس و 0 ورود
def add_user(uid, gid, nid, rose):
    uid, gid = str(uid), str(gid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "money": 100, "roses": 0}  # يبدأ المستخدم بـ 100 فلوس و 0 وردة
    save_data(rose)

# شراء الورود وتسجيل العدد
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
    add_user(uid, gid, nid, rose)

    current_money = rose[gid][uid]["money"]  # الرصيد الحالي
    cost_per_rose = 2  # كل وردة = 2 فلوس
    total_cost = number * cost_per_rose  # حساب التكلفة الإجمالية

    if current_money >= total_cost:
        # خصم الفلوس وزيادة عدد الورود
        rose[gid][uid]["money"] -= total_cost
        rose[gid][uid]["roses"] += number
        save_data(rose)
        await event.reply(f"✅ تم شراء {number} وردة لـ {nid} 🌹 بخصم {total_cost} فلوس!")
    
    else:
        # إذا لم يكن لديه فلوس كافية
        await event.reply(f"❌ لا يمكنك شراء {number} وردة، تحتاج إلى {total_cost} فلوس ولكن لديك فقط {current_money} فلوس!")

# تنزيل الورود (بدون استرجاع فلوس)
@ABH.on(events.NewMessage(pattern=r'تنزيل وردة\s+(\d+)'))
async def remove_rose_handler(event):
    number = int(event.pattern_match.group(1))  # عدد الورود المراد تنزيلها
    message = await event.get_reply_message()

    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لتنزيل الوردة!")
        return
    
    uid = str(message.sender_id)
    nid = message.sender.first_name or "مجهول"
    gid = str(event.chat_id)

    # إضافة المستخدم إذا لم يكن موجودًا
    add_user(uid, gid, nid, rose)

    current_roses = rose[gid][uid]["roses"]  # عدد الورود الحالية

    if current_roses >= number:
        # تقليل عدد الورود بدون استرجاع الفلوس
        rose[gid][uid]["roses"] -= number
        save_data(rose)
        await event.reply(f"✅ تم تنزيل {number} وردة لـ {nid} 🌹!")
    
    else:
        # إذا حاول تنزيل أكثر مما رفع
        await event.reply(f"❌ لا يمكنك تنزيل {number} وردة، لديك فقط {current_roses} وردة!")

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
