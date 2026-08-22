from Resources import *
from ABH import ABH as client
import uuid, re
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
    await asyncio.sleep(0.8)

    if gid in processed_albums:
      return
    processed_albums.add(gid)

    # استخراج الرسائل الخاصة بهذا الألبوم للتعامل معها
    messages = album_buffers[gid]
    print(
        f"تم استلام ألبوم يحتوي على {len(messages)} عناصر برقم المجموعة:"
        f" {gid}"
    )

    # الرد على أول رسالة في الألبوم (أو يمكنك الرد على الكل بحسب رغبتك)
    await messages[0].reply(
        "تم استلام ألبوم الميديا بنجاح! عدد العناصر:" f" {len(messages)}"
    )

    # تنظيف الذاكرة المؤقتة بعد فترة
    await asyncio.sleep(10)
    album_buffers.pop(gid, None)
    processed_albums.discard(gid)

  # الحالة الثانية: إذا كانت رسالة ميديا مفردة (وليست ألبوم)
  else:
    print(f"تم استلام ميديا مفردة برقم الرسالة: {event.id}")
    await event.reply("تم استلام ملف الميديا بنجاح!")


client.start()
client.run_until_disconnected()
