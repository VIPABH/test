from telethon import events
from ABH import *
@ABH.on(events.NewMessage)
async def mx(event):
    for i in range(385, 432):
        x = await ABH.get_message("x04ou", i)
        if x:
            msg = f'{i} موجود'
        else:
            msg = f'{i} غير موجود'
    await event.reply(msg)
