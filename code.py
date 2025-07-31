from telethon import events, Button
from ABH import ABH
@ABH.on(events.NewMessage(pattern=r'^ازعاج (\d+)$'))
async def spam(event):
    await event.reply("تم التعرف على الأمر!")
