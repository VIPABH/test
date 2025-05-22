from telethon import TelegramClient, events, Button
from Resources import mention #type: ignore
import asyncio, os, random, uuid
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

@ABH.on(events.NewMessage(pattern='^تقييد عام$'))
async def start(event):
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة العضو الذي تريد تقييده.")    
    sender = await r.get_sender()
    chat = await event.get_chat()
    participant = await ABH(GetParticipantRequest(
        channel=chat.id,
        user_id=sender.id
))
    if isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
        return await event.reply("⚠️ أنت مشرف أو مالك، لا يمكنك استخدام هذا الأمر.")    
    user_to_restrict = await r.get_sender()
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True
    )
    try:
        await ABH(EditBannedRequest(
            channel=chat.id,
            participant=user_to_restrict.id,
            banned_rights=rights
        ))
        await event.reply(f"✅ تم تقييد {user_to_restrict.first_name} من إرسال الرسائل.")
    except Exception as e:
        await event.reply(f"❌ فشل التقييد: {e}")
ABH.run_until_disconnected()
