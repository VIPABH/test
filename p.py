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
    except FileNotFoundError:
        return {}

# حفظ النقاط في الملف
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل البيانات عند بدء التشغيل
rose = load_points()

# إضافة النقاط
def add_points(uid, gid, nid):
    uid, gid, nid = str(uid), str(gid), str(nid)
    
    if uid not in rose:
        rose[uid] = {}  # إنشاء مستخدم جديد
    
    if gid not in rose[uid]:
        rose[uid][gid] = {}  # إنشاء مجموعة جديدة للمستخدم
    
    if nid not in rose[uid][gid]:
        rose[uid][gid][nid] = 1  # إضافة نقطة جديدة
    else:
        rose[uid][gid][nid] += 1  # زيادة النقاط
    
    save_points(rose)  # حفظ التحديثات في الملف

# حدث عند إرسال "رفع وردة"
@ABH.on(events.NewMessage(pattern='رفع وردة'))
async def rose_handler(event):
    message = await event.get_reply_message()
    if message:
        uid = message.sender_id
        nid = message.sender.first_name  # تصحيح الحصول على الاسم الأول
        chat = str(event.chat_id)  # تحويل ID الدردشة إلى نص

        add_points(uid, chat, nid)
        await event.reply(f"تم رفع الوردة لـ {nid} 🌹")

# حدث عند إرسال "الوراريد"
@ABH.on(events.NewMessage(pattern='الوراريد'))
async def show_handler(event):
    response = "🌹 قائمة الورود 🌹\n"
    for uid, groups in rose.items():
        for gid, names in groups.items():
            for nid, count in names.items():
                response += f"👤 {nid} ({count} وردة) في المجموعة {gid}\n"
    
    await event.reply(response if response else "🚫 لا يوجد أي ورود حتى الآن.")

# تشغيل البوت
ABH.run_until_disconnected()
