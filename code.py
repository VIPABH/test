from telethon.tl.types import DocumentAttributeVideo
from telethon import events
from ABH import ABH

@ABH.on(events.NewMessage)
async def start(e):
    if e.message.media:

        ttl = 30   # القيمة الافتراضية للصور والوسائط العادية

        # التحقق إذا كانت الوسائط Video
        if hasattr(e.message.media, "document") and e.message.media.document:
            for attr in e.message.media.document.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    ttl = attr.duration or 30
                    break

        await ABH.send_file(
            e.chat_id,
            file=e.message.media,
            ttl=int(ttl)
        )
