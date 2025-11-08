from telethon import events, types
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH
import asyncio


@ABH.on(events.Raw)
async def monitor_bot_status(event):
    """يراقب وضع البوت فقط عند التغيير بالإدارة أو الطرد"""
    me = await ABH.get_me()

    update = getattr(event, "update", event)

    # ---------------------------------------------
    # عند تعديل مشاركة البوت في القناة (رفع/تنزيل/طرد)
    # ---------------------------------------------
    if isinstance(update, types.UpdateChannelParticipant):
        participant = update.participant

        # 🟢 رفع البوت مشرف
        if isinstance(participant, types.ChannelParticipantAdmin) and participant.user_id == me.id:
            entity = await ABH.get_entity(update.channel_id)
            await ABH.send_message(entity, "✅ تم رفع البوت كمشرف.")

        # 🔴 تنزيل أو طرد البوت
        elif isinstance(participant, (types.ChannelParticipantBanned, types.ChannelParticipantLeft)) and getattr(participant, "user_id", None) == me.id:
            try:
                entity = await ABH.get_entity(update.channel_id)
                await ABH.send_message(entity, "⚠️ تم طرد أو تنزيل البوت من القناة.")
            except Exception:
                pass
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(update.channel_id))

    # ---------------------------------------------
    # عند إضافة البوت إلى مجموعة عادية (غير قناة)
    # ---------------------------------------------
    elif isinstance(update, types.UpdateChatParticipantAdd):
        if update.user_id == me.id:
            entity = await ABH.get_entity(update.chat_id)
            await ABH.send_message(entity, "✅ تم إضافة البوت إلى المجموعة.")
            await asyncio.sleep(0.5)
            perms = await ABH.get_permissions(update.chat_id, me.id)
            if perms.is_admin:
                await ABH.send_message(entity, "✅ شكراً على الإضافة كمشرف.")
            else:
                await ABH.send_message(entity, "⚠️ لا أستطيع البقاء إلا إذا كنت مشرفاً.")
                await asyncio.sleep(1)
                await ABH(LeaveChannelRequest(update.chat_id))

    # ---------------------------------------------
    # عند حذف البوت من مجموعة عادية
    # ---------------------------------------------
    elif isinstance(update, types.UpdateChatParticipantDelete):
        if update.user_id == me.id:
            entity = await ABH.get_entity(update.chat_id)
            await ABH.send_message(entity, "⚠️ تم طرد البوت من المجموعة.")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(update.chat_id))
