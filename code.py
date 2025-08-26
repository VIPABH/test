from telethon import events
from ABH import ABH
import os

def save(data, filename='data.txt'):
    # إذا الملف موجود نفتح بإضافة + قراءة
    # إذا ما موجود، نفتح بكتابة + قراءة
    mode = 'a+' if os.path.exists(filename) else 'w+'
    with open(filename, mode, encoding='utf-8') as f:
        f.write(f'{data}, \n')
        f.seek(0)  # نرجع المؤشر للبداية حتى نكدر نقرا
        return f.read()

@ABH.on(events.NewMessage)
async def all(e):
    if e.text == 'مل':
        r = await e.get_reply_message()
        if r and r.text:
            x = save(r.text, filename='data.txt')
            await e.reply("تم الحفظ ✅")
            await e.reply("x)
        else:
            await e.reply("رد على رسالة نصية حتى أحفظها ❌")
