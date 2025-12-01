from telethon.tl.types import DocumentAttributeVideo
from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage)
async def start(e):
    if e.message.media:
        duration = None
        for attr in e.message.media.document.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                duration = attr.duration
                break
        
        if duration is None:
            duration = 30   # قيمة افتراضية إذا لم يوجد

        await ABH.send_file(
            e.chat_id,
            file=e.message.media,
            ttl=int(duration)
        )
