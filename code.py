from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import types, events
from Resources import *
from ABH import ABH
import asyncio

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        print("🔹 حدث جديد تم استلامه")

        # # نتأكد أن هذا الحدث من نوع UpdateChannelParticipant فقط
        # if not isinstance(event, types.UpdateChannelParticipant):
        #     print("⏩ هذا الحدث ليس UpdateChannelParticipant، تم تجاهله")
        #     return

        me = await ABH.get_me()
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        if not participant:
            print("⏩ لا يوجد participant في الحدث")
            return

        user_id = participant.user_id
        print(f"🔹 معرف البوت: {me.id}, معرف المستخدم في الحدث: {user_id}, معرف القناة: {channel_id}")

        if user_id != me.id:
            print("⏩ هذا الحدث ليس عن البوت، تم تجاهله")
            return

        # حالة الإضافة كمشرف
        if isinstance(participant, types.ChannelParticipantAdmin):
            print(f"✅ تم إضافة البوت كمشرف: {user_id}")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "✅ شكرًا، تم تفعيل صلاحيات المشرف للبوت!")

        # حالة الإضافة كعضو عادي
        elif isinstance(participant, types.ChannelParticipant):
            print(f"⚠️ تم إضافة البوت كعضو عادي: {user_id} → سيتم الخروج")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "⚠️ لا يمكنني العمل كعضو عادي، سأغادر القناة الآن.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

        # حالة إزالة أو تنزيل البوت
        elif isinstance(participant, (types.ChannelParticipantLeft, types.ChannelParticipantBanned)):
            print(f"⚠️ تم إزالة البوت أو تنزيله من المشرفين: {user_id} → سأغادر")
            entity = await ABH.get_entity(channel_id)
            await ABH.send_message(entity, "⚠️ تم إزالة صلاحياتي كمشرف، سأغادر القناة الآن.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))

    except Exception as e:
        print("❌ حدث خطأ:", e)
