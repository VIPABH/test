from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon import events
from ABH import ABH
@ABH.on(events.NewMessage(pattern='^امسح$'))
async def deletmedia(event):
        chat = event.chat_id
        deleted_count = 0
        async for msg in ABH.iter_messages(chat, reverse=False):
            if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                try:
                    await ABH.delete_messages(chat, msg.id)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ فشل حذف الرسالة {msg.id}: {e}")
        await event.respond(f"✅ تم حذف {deleted_count} رسالة تحتوي على وسائط.")
