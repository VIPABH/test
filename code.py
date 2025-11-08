from telethon import events
from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantBanned
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.utils import get_display_name
from Resources import *
from ABH import ABH
import asyncio
@ABH.on(events.Raw)
async def monitor_everything(event):
    print(type(event))
    me = await ABH.get_me()
    user_id = getattr(event, "user_id", getattr(getattr(event, "participant", None), "user_id", None))
    if not user_id == me.id:
        return
    channel_id = getattr(event, "channel_id", None)
    try:
        entity = await ABH.get_entity(channel_id)
        perms = await ABH.get_permissions(channel_id, me.id)
        if perms.is_admin:
            await ABH.send_message(entity, f"✅ اشكرك على الإضافة ")
        else:
            await ABH.send_message(entity, "⚠️ عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
    except Exception as e:
        print(f"⚠️ خطأ أثناء التحقق من الصلاحيات أو إرسال الرسائل: {e}")
