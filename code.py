from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon import events
from ABH import ABH
@client.on(events.NewMessage(pattern='^امسح$'))
async def delete_all_media(event):
    chat = event.chat_id
    deleted_count = 0
    async for msg in client.iter_messages(chat):
        if msg.media:
            try:
                await client.delete_messages(chat, msg.id)
                deleted_count += 1
            except Exception:
                pass
    await event.respond(f"✅ تم حذف {deleted_count} وسائط.")

