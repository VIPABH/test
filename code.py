from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import UpdateChannelParticipant
from telethon import events
from ABH import ABH
import asyncio
@ABH.on(events.Raw)
async def monitor_restriction(event):
    if not isinstance(event, UpdateChannelParticipant):
        return
    try:
        me = await ABH.get_me()
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", None) or getattr(participant, "user_id", None)
        if user_id is None and hasattr(event, "chat_id"):
            user_id = me.id
            channel_id = event.chat_id
        if user_id != me.id or channel_id is None:
            return
        perms = await ABH.get_permissions(entity, me.id)
        if not perms.is_admin:
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "البوت عنده قيود 👋")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
    except Exception as e:
        print(e)
        return
