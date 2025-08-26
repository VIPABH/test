from telethon import events
from ABH import ABH
import os

def save(data, filename):
    mode = 'a+' if os.path.exists(filename) else 'w+'
    with open(filename, mode, encoding='utf-8') as f:
        f.write(f'{data}, \n')
        f.seek(0)
        return f.read()
@ABH.on(events.NewMessage)
async def all(e):
    if e.text == 'مل':
        r = await e.get_reply_message()
        if r and r.sender_id:
            x = save(r.sender_id, filename='d.json')
            await e.reply("تم الحفظ ✅")
            await e.reply(x)
        else:
            await e.reply("رد على رسالة نصية حتى أحفظها ❌")
