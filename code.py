from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from ABH import ABH  # تأكد أن ABH معرف باستخدام bot token

@ABH.on(events.NewMessage(pattern='^امسح$'))
async def delete_bot_media(event):
    chat = event.chat_id
    deleted_count = 0

    await event.respond("🔄 جاري حذف الوسائط التي أرسلها البوت...")

    # فقط رسائل البوت نفسه
    async for msg in ABH.iter_messages(chat, from_user='me'):
        if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            try:
                await ABH.delete_messages(chat, msg.id)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ فشل حذف الرسالة {msg.id}: {e}")

    await event.respond(f"✅ تم حذف {deleted_count} رسالة تحتوي على وسائط أرسلها البوت.")
