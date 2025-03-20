import os
from telethon import TelegramClient, events

# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# تهيئة بوت تيليجرام
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قاموس لتخزين النقاط للمستخدمين
points = {}

@ABH.on(events.NewMessage)
async def p(event):
    global points

    # الحصول على معرف المستخدم والمجموعة واسم المستخدم
    uid = event.sender_id
    gid = event.chat_id
    nid = event.sender.username if event.sender.username else "Unknown"

    # التحقق مما إذا كان المستخدم موجودًا في القاموس وإلا يتم إضافته
    if uid not in points:
        points[uid] = {"nid": nid, "gid": gid, "points": 0}

    # زيادة النقاط
    points[uid]["points"] += 2

    # إرسال عدد النقاط الحالي للمستخدم
    await event.reply(f'🎯 {nid} لديك الآن {points[uid]["points"]} نقاط!')

# تشغيل البوت
ABH.run_until_disconnected()
