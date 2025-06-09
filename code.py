from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from ABH import ABH

# قاموس لتخزين رسائل الوسائط (مفاتيح: chat_id، قيم: list من message_id)
media_messages = {}

@ABH.on(events.NewMessage())
async def store_media_messages(event):
    chat_id = event.chat_id
    msg = event.message

    if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
        if chat_id not in media_messages:
            media_messages[chat_id] = []
        media_messages[chat_id].append(msg.id)

@ABH.on(events.NewMessage(pattern='^امسح$'))
async def delete_stored_media(event):
    chat_id = event.chat_id
    deleted_count = 0

    await event.respond("🔄 جاري حذف الوسائط المخزنة...")

    if chat_id in media_messages:
        for msg_id in media_messages[chat_id]:
            try:
                await ABH.delete_messages(chat_id, msg_id)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ فشل حذف الرسالة {msg_id}: {e}")

        # بعد الحذف نفرغ القاموس
        media_messages[chat_id] = []

    await event.respond(f"✅ تم حذف {deleted_count} رسالة وسائط.")
