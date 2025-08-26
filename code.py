from telethon import events
from ABH import ABH
import os, json

def save(data, filename='data.txt'):
    if not os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            f.write(f'{data}, \n')
            load = f.read()
            return load
    else:
        with open(filename, 'r', encoding='utf-8') as f:
            f.write(f'{data}, \n')
            load = f.read()
            return load
@ABH.on(events.NewMessage)
async def all(e):
    t = e.text
    if t == 'مل':
        r = await e.get_reply_message()
        if r:
            x = save(r.text, filename='data.txt')
            await e.reply("تم الحفظ ✅")
            await e.reply(x)
        else:
            await e.reply("رد على رسالة حتى أحفظها ❌")
