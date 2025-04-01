import os
import json
from telethon import TelegramClient, events

# جلب القيم من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل النقاط من الملف
def load_points(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# حفظ النقاط في الملف
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل البيانات عند بدء التشغيل
rose = load_points()

# إضافة النقاط
def add_points(uid, gid, nid, rose):
    uid, gid, nid = str(uid), str(gid), str(nid)
    
    if gid not in rose:
        rose[gid] = {}  # إنشاء مجموعة جديدة
    
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "count": 1}  # إضافة مستخدم جديد مع أول وردة
    else:
        rose[gid][uid]["count"] += 1  # زيادة النقاط
    
    save_points(rose)  # حفظ التحديثات في الملف

# حدث عند إرسال "رفع وردة"
@ABH.on(events.NewMessage(pattern='رفع وردة'))
async def rose_handler(event):
    message = await event.get_reply_message()
    
    if not message or not message.sender:
        await event.reply("❌ يجب الرد على رسالة شخص لرفع الوردة!")
        return
    
    uid = message.sender_id
    nid = message.sender.first_name or "مجهول"  # تجنب الخطأ إذا لم يكن هناك اسم
    chat = str(event.chat_id)  # تحويل ID المجموعة إلى نص

    add_points(uid, chat, nid, rose)  # تمرير `rose` لضمان التحديث الصحيح
    await event.reply(f"✅ تم رفع الوردة لـ {nid} 🌹")

# حدث عند إرسال "الوراريد"
@ABH.on(events.NewMessage(pattern='الوراريد'))
async def show_handler(event):
    chat_id = str(event.chat_id)  # استخراج معرف المجموعة

    if chat_id not in rose or not rose[chat_id]:
        await event.reply("🚫 لا يوجد أي ورود في هذه المجموعة حتى الآن.")
        return

    response = f"🌹 قائمة الورود في هذه المجموعة ({chat_id}) 🌹\n"
    for uid, data in rose[chat_id].items():
        response += f"👤 {data['name']}: {data['count']} وردة\n"

    await event.reply(response)

# تشغيل البوت
ABH.run_until_disconnected()
