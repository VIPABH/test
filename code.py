from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def scan(event):
    x = 'x04ou'
    for i in range(385):
        m = f'https://t.me/x04ou/{i}'
        s = await ABH.get_messag(m)
        if not s.media:
            await event.reply(s)
