from telethon.errors import UserIsBlockedError, PeerIdInvalidError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import events, Button, types
from ABH import ABH
@ABH.on(events.Raw)
async def monitor_everything(event):
    try:
        me = await ABH.get_me()
        channel_id = getattr(event, "channel_id", None)
        participant = getattr(event, "participant", None)
        user_id = getattr(event, "user_id", getattr(participant, "user_id", None))
        if user_id != me.id or channel_id is None or participant is None:
            return
        if isinstance(participant, types.ChannelParticipantRestricted):
            try:
                entity = await ABH.get_entity(channel_id)
                await ABH.send_message(entity, "هاا تقييد؟ يله بيباي 👋")
            except Exception:
                pass
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
            return
        update = getattr(event, "update", event)
        actor_id = getattr(update, "actor_id", None) or getattr(update, "user_id", None)
        actor = await ABH.get_entity(actor_id)
        mention = f"[{actor.first_name}](tg://user?id={actor.id})"
        entity = await ABH.get_entity(channel_id)
        perms = await ABH.get_permissions(channel_id, me.id)
        message = await ABH.get_messages("recoursec", ids=22)
        chat = await event.get_input_chat()
        full_chat = await ABH(GetFullChatRequest(chat.chat_id))
        count = full_chat.full_chat.participants_count
        # if count < 50:
        #     await ABH(LeaveChannelRequest(channel_id))
        #     return
        if perms.is_admin:
            x = await ABH.send_file(entity, message.media)
            await ABH.send_message(entity, f"اشكرك على الاضافة وردة ( {mention} ) ", reply_to=x.id)
        else:
            await ABH.send_message(entity, "😢")
            await asyncio.sleep(1)
            await ABH(LeaveChannelRequest(channel_id))
    except Exception as e:
        print(e)
        return
