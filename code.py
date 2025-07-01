from telethon import events
from ABH import ABH
from telethon.tl.types import DocumentAttributeAudio
import asyncio
x = []
z = []
@ABH.on(events.NewMessage)
async def scan(event):
    channel = 'x04ou'
    for i in range(1, 386):
        try:
            msg = await ABH.get_messages(channel, ids=i)
            if not msg:
                await event.reply(f'الرساله غير موجوده {i}')
                x.append(i)
            if not msg.media or not msg.document:
                await event.reply(f'الرساله لا تحتوي علئ ملف {i}')
                x.append(i)
                continue
            for attr in msg.document.attributes:
                if isinstance(attr, DocumentAttributeAudio) and not attr.voice:
                    z.append(i)
                    break
            await asyncio.sleep(0.3)
        except Exception:
            continue
        await event.reply(f'{x}')
        await event.reply(f'{z}')
