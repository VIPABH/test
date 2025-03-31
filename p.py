import random
import os
import json
from telethon import TelegramClient, events

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إنشاء البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تحميل النقاط من ملف JSON
def load_points(filename="points.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# حفظ النقاط في ملف JSON
def save_points(data, filename="points.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

# تحميل النقاط عند بدء التشغيل
points = load_points()

@ABH.on(events.NewMessage)
async def p(event):
    global points  # استخدام القاموس العام

    uid = str(event.sender_id)  # تأكد من أن المفتاح نصي لتجنب الأخطاء
    gid = str(event.chat_id)
    nid = event.sender.username if event.sender.username else "unknown"

    # التحقق من وجود المستخدم داخل المجموعة في القاموس
    if uid not in points:
        points[uid] = {}

    if gid not in points[uid]:
        points[uid][gid] = {"nid": nid, "points": 0}

    # إضافة 2 نقطة
    points[uid][gid]["points"] += 2

    # حفظ التعديلات في الملف
    save_points(points)

    # إرسال الرد
    await event.reply(f'نقاط {nid}: {points[uid][gid]["points"]}')

# تشغيل البوت
ABH.run_until_disconnected()
