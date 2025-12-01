from telethon.tl.types import DocumentAttributeVideo
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def start(e):
    duration = 30  
    print(e)
    await ABH.send_file(e.chat_id, e.media, ttl=duration)
