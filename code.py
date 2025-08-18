from telethon import events
from ABH import ABH
import os, json
def file(filename, data):
    if not os.path.exists(filename):
        os.mkdir(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            f.write(f'{data}, \n')
@ABH.on(events.NewMessage)
async def all(e):
    t = e.text
    if t == 'مل':
        r = await e.get_reply_message()
        file(r.text, 'test')
        return
