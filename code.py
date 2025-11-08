from telethon import events
from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantBanned
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.utils import get_display_name
from Resources import *
from ABH import ABH

@ABH.on(events.Raw)
async def monitor_everything(event):
    if not user_id == me.id:
        return
    if isinstance(event, UpdateChannelParticipant):
        me = await ABH.get_me()
        channel_id = getattr(event, "channel_id", None)
        user_id = getattr(event, "user_id", getattr(getattr(event, "participant", None), "user_id", None))
        participant = getattr(event, "participant", None)
        if (participant is None or isinstance(participant, ChannelParticipantBanned)):
            print(f"⚠️ البوت تم طرده أو حظره من القناة {channel_id}")
            return
        try:
            entity = await ABH.get_entity(channel_id)
            perms = await ABH.get_permissions(channel_id, me.id)
            if perms.is_admin:
                try:
                    user_entity = await ABH.get_entity(user_id)
                    user_name = get_display_name(user_entity)
                except:
                    user_name = "صديقي"
                await ABH.send_message(entity, f"✅ اشكرك على الإضافة {user_name}")
            else:
                await ABH.send_message(entity, "⚠️ عذرًا، لا أستطيع البقاء هنا إلا إذا كنت مشرفًا.")
                try:
                    await ABH(LeaveChannelRequest(channel_id))
                except Exception as leave_err:
                    print(f"⚠️ خطأ أثناء مغادرة القناة: {leave_err}")
        except Exception as e:
            print(f"⚠️ خطأ أثناء التحقق من الصلاحيات أو إرسال الرسائل: {e}")
