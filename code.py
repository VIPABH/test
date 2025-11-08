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
                await ABH.send_message(entity, "⚠️ عذرًا، تم تنزيل البوت أو طرده، سأغادر القناة.")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(channel_id))
                return
        entity = await ABH.get_entity(channel_id)
        perms = await ABH.get_permissions(channel_id, me.id)
        if perms.is_admin:
            await ABH.send_message(entity, f"✅ اشكرك على الإضافة ")
        else:
            await ABH.send_message(entity, "⚠️ عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
    except:
        return 
