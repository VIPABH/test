from telethon import events
from ABH import ABH
from telethon.tl.types import DocumentAttributeAudio
import asyncio
@ABH.on(events.NewMessage)
async def scan(event):
    channel = 'x04ou'
    for i in range(1, 386):
        try:
            msg = await ABH.get_messages(channel, ids=i)
            if not msg:
                await event.reply(f'الرساله غير موجوده {i}')
            if not msg.media or not msg.document:
                await event.reply(f'الرساله لا تحتوي علئ ملف {i}')
                continue
            for attr in msg.document.attributes:
                if isinstance(attr, DocumentAttributeAudio) and not attr.voice:
                    break
            await asyncio.sleep(0.3)
        except Exception:
            continue 
