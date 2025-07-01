from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def scan(event):
    x = 'x04ou'
    for i in range(385):
        m = f'https://t.me/{x}/{i}'
        s = await ABH.get_messages(x, ids=m)
        if not s.media:
            await event.reply(str(s))
