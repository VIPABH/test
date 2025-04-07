import os, asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityUrl
from telethon.errors import SessionPasswordNeededError

# تحميل المتغيرات البيئية
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

hint_gid = -1002168230471
@ABH.on(events.NewMessage)
async def test(event):
    msg = event.message
    chat = event.chat_id
    if chat != -1001784332159 or msg.sticker:
        return  
    has_media = bool(msg.media)
    has_document = bool(msg.document)
    has_url = any(isinstance(entity, MessageEntityUrl) for entity in (msg.entities or []))
    perms = await ABH.get_permissions(event.chat_id, event.sender_id)
    uid = event.sender_id
    if (has_media or has_document or has_url) and not (perms.is_admin or perms.is_creator):
        sender = await event.get_sender()
        nid = sender.first_name
        msg_link = f"https://t.me/{event.chat.username}/{event.id}" if event.chat.username else None
        message = event.message
        if message.edit_date:
            await ABH.send_message(hint_gid, f'تم #تعديل رسالة مريبة \n رابط الرسالة ↢ **{msg_link}** \n ايدي المستخدم ↢ `{uid}` \n اسم المستخدم ↢ `{nid}` \n تم تعديلها في {message.edit_date}')
            await asyncio.sleep(60)
            await event.delete()
    else:
        return

ABH.run_until_disconnected()
