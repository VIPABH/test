from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantBanned, ChannelParticipantLeft
from telethon import events
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.utils import get_display_name
from Resources import *
from ABH import ABH

@ABH.on(events.Raw)
async def monitor_everything(event):
    # فقط إذا كان التحديث من نوع UpdateChannelParticipant
    if not isinstance(event, UpdateChannelParticipant):
        return

    me = await ABH.get_me()
    channel_id = getattr(event, "channel_id", None)
    user_id = getattr(event, "user_id", getattr(getattr(event, "participant", None), "user_id", None))

    # فقط إذا الحدث يخص البوت
    if user_id == me.id and channel_id:
        # التحقق إذا البوت تم طرده أو حظره
        participant = getattr(event, "participant", None)
        if participant is None or isinstance(participant, ChannelParticipantBanned):
            print(f"⚠️ تم طرد أو حظر البوت من القناة {channel_id}")
            # هنا ممكن تنفذ أي عملية تريدها بعد الطرد، مثل تسجيل الحدث أو إرسال تنبيه
            return

        # لو البوت انضم بشكل عادي، أكمل باقي المنطق
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
                await ABH.send_message(entity, "⚠️ لا أستطيع البقاء هنا إلا إذا كنت مشرفًا.")
                try:
                    await ABH(LeaveChannelRequest(channel_id))
                except Exception as leave_err:
                    print(f"⚠️ خطأ أثناء مغادرة القناة: {leave_err}")

        except Exception as e:
            print(f"⚠️ خطأ أثناء التحقق من الصلاحيات أو إرسال الرسائل: {e}")
