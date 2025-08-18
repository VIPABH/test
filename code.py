from telethon import events
from ABH import ABH
import os, json

def file(filename, data):
    # إذا الملف ما موجود، ننشئه
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'{data}, \n')
    else:
        # إذا الملف موجود، نضيف البيانات بدون حذف القديم
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f'{data}, \n')

@ABH.on(events.NewMessage)
async def all(e):
    t = e.text
    if t == 'مل':
        r = await e.get_reply_message()
        if r:  # نتأكد أن الرسالة رد
            file("data.txt", r.text)  # نخزن الرد داخل ملف data.txt
            await e.reply("تم الحفظ ✅")
        else:
            await e.reply("رد على رسالة حتى أحفظها ❌")
