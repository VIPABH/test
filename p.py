import os, asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityUrl

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

x = set()
hint_gid = -1002168230471
@ABH.on(events.MessageEdited)
async def test(event):
    msg = event.message
    has_media = bool(msg.media)
    has_document = bool(msg.document)
    has_url = any(isinstance(entity, MessageEntityUrl) for entity in (msg.entities or []))
    perms = await ABH.get_permissions(event.chat_id, event.sender_id)
    uid = event.sender_id
    if uid in x:
        return

    if (has_media or has_document or has_url) and not (perms.is_admin or perms.is_creator or uid in x):
        await ABH.send_message(hint_gid, 'ها شعدلت ولك!.')
        await asyncio.sleep(3)
        await event.delete()
    else:
        return

@ABH.on(events.NewMessage(pattern='سماح'))
async def سماح(event):
    uid = event.sender_id
    x.add(uid)

ABH.run_until_disconnected()
