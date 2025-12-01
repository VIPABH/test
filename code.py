from ABH import ABH
from telethon import events
@ABH.on(events.NewMessage)
async def start(e):
    
    await ABH.send_file(e.chat_id, e.media, ttl=e.message.video.duration or 30)
