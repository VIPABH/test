from telethon import TelegramClient, events, types
from telethon.tl.functions.channels import LeaveChannelRequest
from ABH import ABH
import asyncio
async def check_bot_permissions(chat_id):
    me = await ABH.get_me()
    perms = await ABH.get_permissions(chat_id, me.id)
    entity = await ABH.get_entity(chat_id)
    if perms.is_admin:
        await ABH.send_message(entity, "✅ شكراً على الإضافة كمشرف")
    else:
        await ABH.send_message(entity, "⚠️ لا أستطيع البقاء إلا إذا لم أكن مشرفاً.")
        await asyncio.sleep(1)
        await ABH(LeaveChannelRequest(chat_id))
@ABH.on(events.ChatAction)
async def bot_added(event):
    me = await ABH.get_me()
    if event.user_added and me.id in [u.id for u in event.users]:
        await check_bot_permissions(event.chat_id)
@ABH.on(events.ChatAdminUpdated)
async def bot_admin_change(event):
    me = await ABH.get_me()
    if event.user_id != me.id:
        return
    entity = await ABH.get_entity(event.chat_id)
    if event.old_status is None and event.new_status is not None:
        await ABH.send_message(entity, "✅ تم رفع البوت كمشرف")
    elif event.old_status is not None and event.new_status is None:
        await ABH.send_message(entity, "⚠️ تم تنزيل البوت من المشرف")
@ABH.on(events.Raw)
async def bot_removed(event):
    me = await ABH.get_me()
    participant = getattr(event, "participant", None)
    user_id = getattr(event, "user_id", None)
    channel_id = getattr(event, "channel_id", None)
    if user_id != me.id:
        return
    if isinstance(participant, (types.ChannelParticipantLeft, types.ChannelParticipantBanned)):
        entity = await ABH.get_entity(channel_id)
        await ABH.send_message(entity, "⚠️ تم تنزيل البوت أو طرده، سأغادر القناة.")
        await asyncio.sleep(1)
        await ABH(LeaveChannelRequest(channel_id))
