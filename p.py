from telethon import TelegramClient, events
from Resources import mention
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
import os, time
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
restriction_end_times = {}
@ABH.on(events.NewMessage(pattern='^تقييد عام|مخفي قيده|مخفي قيدة$'))
async def restrict_user(event):
    if not event.is_group:
        return
    r = await event.get_reply_message()
    if not r:
        return await event.reply(" يجب الرد على رسالة العضو الذي تريد تقييده.")    
    chat = await event.get_chat()
    sender = await r.get_sender()
    name = await mention(event, sender)
    try:
        participant = await ABH(GetParticipantRequest(channel=chat.id, participant=sender.id))
        if not isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
            return await event.reply(f"لا يمكنك تقييد {name} لانه مشرف ")
    except:
        return
    user_to_restrict = await r.get_sender()
    user_id = user_to_restrict.id
    now = int(time.time())
    restriction_duration = 10 * 60
    restriction_end_times[user_id] = now + restriction_duration
    rights = ChatBannedRights(
        until_date=now + restriction_duration,
        send_messages=True
    )
    try:
        await ABH(EditBannedRequest(channel=chat.id, participant=user_id, banned_rights=rights))
        await event.reply(f" تم تقييد {user_to_restrict.first_name} لمدة 10 دقائق.")
    except Exception as e:
        await event.reply(f" ياريت اقيده بس ماكدر لان مشرف")
@ABH.on(events.NewMessage)
async def monitor_messages(event):
    if not event.is_group:
        return
    user_id = event.sender_id
    now = int(time.time())
    if user_id in restriction_end_times:
        end_time = restriction_end_times[user_id]
        if now < end_time:
            remaining = end_time - now
            try:
                chat = await event.get_chat()
                rights = ChatBannedRights(
                    until_date=now + remaining,
                    send_messages=True
                )
                await ABH(EditBannedRequest(channel=chat.id, participant=user_id, banned_rights=rights))
                await event.reply(f" لا يمكنك إرسال الرسائل الآن. تم إعادة تقييدك لمدة ||{remaining//60} دقيقة و {remaining%60} ثانية.||")
            except:
                pass
ABH.run_until_disconnected()
