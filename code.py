import asyncio
import re
import uuid
from ABH import ABH as client
from Resources import *
from telethon import events

processed_albums = set()
album_buffers = {}


@client.on(events.NewMessage(incoming=True))
async def handle_media(event):
  # التحقق مما إذا كانت الرسالة تحتوي على ميديا (صورة، فيديو، إلخ)
  if not event.media:
    return

  # الحالة الأولى: إذا كانت الرسالة تنتمي لمجموعة (ألبوم)
  if event.grouped_id:
    gid = event.grouped_id

    if gid in processed_albums:
      return  # تم الرد على هذا الألبوم مسبقاً

    if gid not in album_buffers:
      album_buffers[gid] = []

    album_buffers[gid].append(event)

    # انتظار قصير (0.8 ثانية) لتجميع باقي صور/ملفات الألبوم الواصلة

    if gid in processed_albums:
      return
    processed_albums.add(gid)

    # استخراج الرسائل الخاصة بهذا الألبوم للتعامل معها
    messages = album_buffers[gid]

    # الرد على أول رسالة في الألبوم
    await messages[0].reply(
        f"تم استلام ألبوم الميديا بنجاح! عدد العناصر: {len(messages)}"
    )

    # تنظيف الذاكرة المؤقتة بعد فترة
    await asyncio.sleep(10)
    album_buffers.pop(gid, None)
    processed_albums.discard(gid)

  # الحالة الثانية: إذا كانت رسالة ميديا مفردة (وليست ألبوم)
  else:
    await event.reply(f"تم استلام ميديا مفردة برقم الرسالة: {event.id}")
