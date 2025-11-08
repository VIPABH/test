# ======================================================
#      كود مراقبة وضع البوت عبر events.Raw فقط
# ======================================================

from telethon import TelegramClient, events, types
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH
import asyncio


@ABH.on(events.Raw)
async def bot_status_monitor(event):
    me = await ABH.get_me()

    # ----------------------------------------------
    # 1️⃣ عند إضافة البوت إلى مجموعة / قناة
    # ----------------------------------------------
    if isinstance(event, types.UpdateChatParticipantAdd):
        if event.user_id == me.id:
            entity = await ABH.get_entity(event.chat_id)
            await ABH.send_message(entity, "✅ تم إضافة البوت إلى المجموعة.")
            await asyncio.sleep(0.5)
            perms = await ABH.get_permissions(event.chat_id, me.id)
            if perms.is_admin:
                await ABH.send_message(entity, "✅ شكراً على الإضافة كمشرف.")
            else:
                await ABH.send_message(entity, "⚠️ لا أستطيع البقاء إلا إذا كنت مشرفاً.")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(event.chat_id))

    # ----------------------------------------------
    # 2️⃣ عند طرد أو حظر البوت من المجموعة / القناة
    # ----------------------------------------------
    elif isinstance(event, types.UpdateChatParticipantDelete):
        if event.user_id == me.id:
            entity = await ABH.get_entity(event.chat_id)
            await ABH.send_message(entity, "⚠️ تم طرد البوت من المجموعة.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(event.chat_id))

    elif isinstance(event, types.UpdateChannelParticipant):
        participant = getattr(event, "participant", None)
        if isinstance(participant, (types.ChannelParticipantBanned, types.ChannelParticipantLeft)):
            user_id = getattr(participant, "user_id", None)
            if user_id == me.id:
                try:
                    entity = await ABH.get_entity(event.channel_id)
                    await ABH.send_message(entity, "⚠️ تم طرد أو حظر البوت من القناة.")
                except Exception:
                    pass
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(event.channel_id))

    # ----------------------------------------------
    # 3️⃣ عند رفع أو تنزيل البوت من الإشراف
    # ----------------------------------------------
    elif isinstance(event, types.UpdateChannelParticipant):
        participant = getattr(event, "participant", None)
        if isinstance(participant, types.ChannelParticipantAdmin):
            if participant.user_id == me.id:
                entity = await ABH.get_entity(event.channel_id)
                await ABH.send_message(entity, "✅ تم رفع البوت كمشرف.")
        elif isinstance(participant, types.ChannelParticipant):
            if getattr(participant, "user_id", None) == me.id:
                entity = await ABH.get_entity(event.channel_id)
                await ABH.send_message(entity, "⚠️ تم تنزيل البوت من الإشراف.")


# ======================================================
# ✅ نهاية الكود
# ======================================================
