from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import types, events
from Resources import *
from ABH import ABH
import asyncio

@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        print("🔹 حدث جديد تم استلامه")  # بداية الحدث
        me = await ABH.get_me()
        print(f"🔹 معرف البوت: {me.id}")

        # جلب user_id من الحدث
        user_id = getattr(event, "user_id", getattr(getattr(event, "participant", None), "user_id", None))
        print(f"🔹 معرف المستخدم في الحدث: {user_id}")

        # إذا الحدث ليس عن البوت نفسه تجاهل
        if not user_id == me.id:
            print("⏩ هذا الحدث ليس عن البوت، تم تجاهله")
            return

        channel_id = getattr(event, "channel_id", None)
        print(f"🔹 معرف القناة: {channel_id}")

        participant = getattr(event, "participant", None)
        if not participant:
            print("⏩ لا يوجد participant في الحدث")
            return

        # حالات البوت: إضافة/إزالة/ترقية
        if isinstance(participant, (types.ChannelParticipant, types.ChannelParticipantAdmin, 
                                    types.ChannelParticipantLeft, types.ChannelParticipantBanned)):
            print("🔹 الحدث متعلق بتغيير صلاحيات البوت أو إضافته")

            # حالة الإضافة كمشرف
            if isinstance(participant, types.ChannelParticipantAdmin):
                print(f"✅ تم إضافة البوت كمشرف: {participant.user_id}")
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, f"✅ شكرًا، تم تفعيل صلاحيات المشرف للبوت!")

            # حالة الإضافة كعضو عادي → يمنع ويغادر
            elif isinstance(participant, types.ChannelParticipant):
                print(f"⚠️ تم إضافة البوت كعضو عادي: {participant.user_id} → سيتم الخروج")
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "⚠️ لا يمكنني العمل كعضو عادي، سأغادر القناة الآن.")
                await asyncio.sleep(1)
                print("🚪 يغادر البوت القناة")
                await ABH(LeaveChannelRequest(channel_id))

            # حالة إزالة البوت أو تنزيله من المشرف
            elif isinstance(participant, (types.ChannelParticipantLeft, types.ChannelParticipantBanned)):
                print(f"⚠️ تم إزالة البوت أو تنزيله من المشرفين: {participant.user_id} → سأغادر")
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "⚠️ تم إزالة صلاحياتي كمشرف، سأغادر القناة الآن.")
                await asyncio.sleep(1)
                print("🚪 يغادر البوت القناة بعد إزالة الصلاحيات")
                await ABH(LeaveChannelRequest(channel_id))

        else:
            print("⏩ الحدث ليس متعلق بإضافة أو إزالة البوت")

    except Exception as e:
        print("❌ حدث خطأ:", e)
