from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import types, events
from Resources import *
from ABH import ABH
import asyncio
@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        me = await ABH.get_me()
        user_id = getattr(event, "user_id", getattr(getattr(event, "participant", None), "user_id", None))
        if not user_id == me.id:
            return
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        if isinstance(participant, (types.ChannelParticipant, types.ChannelParticipantAdmin)):
            if isinstance(participant, (types.ChannelParticipantLeft, types.ChannelParticipantBanned)):
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "خلي يفيدوكم يله بيباي")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))
                return
        update = getattr(event, "update", event)
        actor_id = getattr(update, "actor_id", None) or getattr(update, "user_id", None)
        actor = await ABH.get_entity(actor_id)
        mention = f"[{actor.first_name}](tg://user?id={actor.id})"
        entity = await ABH.get_entity(channel_id)
        perms = await ABH.get_permissions(channel_id, me.id)
        if perms.is_admin:
            await ABH.send_file(
                entity,
                'resources/AnimatedSticker.tgs')
            await ABH.send_message(entity, f"اشكرك على الاضافة وردة {mention}")
        else:
            await ABH.send_message(entity, "😢")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
    except:
        return
