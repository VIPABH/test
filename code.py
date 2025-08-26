from telethon import events
from ABH import ABH
import os, json

def save(data, filename='data.txt'):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'{data}, \n')
    else:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f'{data}, \n')
@ABH.on(events.NewMessage)
async def all(e):
    t = e.text
    if t == 'مل':
        r = await e.get_reply_message()
        if r:
            save(r.text, filename='data.txt')
            await e.reply("تم الحفظ ✅")
        else:
            await e.reply("رد على رسالة حتى أحفظها ❌")
