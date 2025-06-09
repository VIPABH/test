import json
import os
from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from ABH import ABH
FILE_PATH = "media_messages.json"
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        media_messages = json.load(f)
else:
    media_messages = {}
def save_media_messages():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(media_messages, f, ensure_ascii=False, indent=2)
@ABH.on(events.NewMessage())
async def store_media_messages(event):
    chat_id = str(event.chat_id)
    msg = event.message
    if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
        if chat_id not in media_messages:
            media_messages[chat_id] = []
        if msg.id not in media_messages[chat_id]:
            media_messages[chat_id].append(msg.id)
            save_media_messages()
@ABH.on(events.NewMessage(pattern='^امسح$'))
async def delete_stored_media(event):
    chat_id = str(event.chat_id)
    deleted_count = 0
    await event.respond("🔄 جاري حذف الوسائط المخزنة...")
    if chat_id in media_messages and media_messages[chat_id]:
        for msg_id in media_messages[chat_id]:
            try:
                await ABH.delete_messages(int(chat_id), msg_id)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ فشل حذف الرسالة {msg_id}: {e}")
        media_messages[chat_id] = []
        save_media_messages()
    await event.respond(f" تم حذف {deleted_count} رسالة وسائط.")
@ABH.on(events.NewMessage(pattern='^عدد$'))
async def count_media_messages(event):
    chat_id = str(event.chat_id)
    if chat_id in media_messages and media_messages[chat_id]:
        count = len(media_messages[chat_id])
        await event.respond(f"📊 يوجد {count} رسالة وسائط مخزنة في هذه المحادثة.")
    else:
        await event.respond("ℹ️ لا توجد أي رسائل وسائط مخزنة حالياً في هذه المحادثة.")
@ABH.on(events.NewMessage(pattern='^ثبتها|الغاء منع من المسح|الغاء مسح$'))
async def undel(event):
    r = await event.get_reply_message()
    if not r:
        await event.reply('❗ يجب الرد على رسالة وسائط.')
        return
    chat_id = str(event.chat_id)
    msg_id = r.id
    if chat_id in media_messages and msg_id in media_messages[chat_id]:
        media_messages[chat_id].remove(msg_id)
        save_media_messages()
        await event.reply("✅ تم استثناء هذه الرسالة من الحذف.")
    else:
        await event.reply("ℹ️ هذه الرسالة غير مسجلة للحذف أو تم حذفها مسبقًا.")
