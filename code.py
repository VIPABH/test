import asyncio
import re
import uuid
from ABH import ABH as client
from Resources import *
from telethon import events


@client.on(events.NewMessage(incoming=True))
async def handle_media(event):
  # التحقق مما إذا كانت الرسالة تحتوي على ميديا (صورة، فيديو، إلخ)
  if not event.media:
    return

  # إذا كانت تنتمي لمجموعة (ألبوم) أو رسالة مفردة، يتم الرد عليها فوراً لكل رسالة تصل
  if event.grouped_id:
    await event.reply(
        f"تم استلام عنصر من ألبوم (Group ID: {event.grouped_id}) - رقم الرسالة:"
        f" {event.id}"
    )
  else:
    await event.reply(f"تم استلام ميديا مفردة برقم الرسالة: {event.id}")
