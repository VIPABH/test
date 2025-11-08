from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import types, events
from ABH import ABH
import asyncio
@ABH.on(events.Raw)
async def monitor_bot_permissions(event):
    try:
        me = await ABH.get_me()
        channel_id = getattr(event, "channel_id", None)

        # نتحقق أن الحدث يتعلق بالبوت نفسه
        participant = getattr(event, "participant", None)
        if not participant:
            return
        user_id = getattr(participant, "user_id", None)
        if user_id != me.id:
            return

        # حالة البوت تمت إضافته أو ترقيته
        if isinstance(participant, types.ChannelParticipantAdmin):
            print(f"✅ تم إضافة البوت كمشرف في القناة {channel_id}")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "✅ شكرًا، تم تفعيل صلاحيات المشرف للبوت!")

        # حالة البوت تمت إضافته كعضو عادي → يمنع ذلك
        elif isinstance(participant, types.ChannelParticipant):
            print(f"⚠️ تمت إضافة البوت كعضو عادي في القناة {channel_id} → سيتم الخروج")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "⚠️ لا يمكنني العمل كعضو عادي، سأغادر القناة الآن.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

        # حالة تم تنزيل البوت من المشرف → يحذر ويغادر
        elif isinstance(participant, types.ChannelParticipantLeft) or isinstance(participant, types.ChannelParticipantBanned):
            print(f"⚠️ تم إزالة البوت أو تنزيله من المشرفين في القناة {channel_id} → سأغادر")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "⚠️ تم إزالة صلاحياتي كمشرف، سأغادر القناة الآن.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

    except Exception as e:
        print("حدث خطأ:", e)
