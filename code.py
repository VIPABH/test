from telethon.tl.types import DocumentAttributeVideo
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage)
async def start(e):
    duration = 30  
    if e.message.media and hasattr(e.message.media, 'document'):
        for attr in e.message.media.document.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                duration = attr.duration
                break    
    await ABH.send_file(e.chat_id, e.media, ttl=duration)
