from telethon.tl.functions.channels import GetFullChannelRequest, LeaveChannelRequest
from telethon.tl.types import UpdateChannelParticipant
from telethon import events
from Resources import *
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
        entity = await ABH.get_entity(channel_id)
        perms = await ABH.get_permissions(entity, me.id)
        group_name = getattr(entity, "title", None)
        full = await ABH(GetFullChannelRequest(channel_id))
        link = None
        if hasattr(full.full_chat, "exported_invite") and full.full_chat.exported_invite:
            if hasattr(full.full_chat.exported_invite, "link"):
                link = full.full_chat.exported_invite.link
                if not perms.is_admin:
                    await ABH.send_message(entity, "ها صارت بيها تقييد مو😁؟ سهله")
                    await hint(f"خرجت من مجموعة ( {group_name} ) \n ايديها ( {channel_id} ) \n الرابط ( {link} )")
                    await asyncio.sleep(1)
                    await ABH(LeaveChannelRequest(channel_id))
    except Exception as e:
        print(e)
        return
