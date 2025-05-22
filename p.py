from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
import os

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='^تقييد عام$'))
async def start(event):
    if not event.is_group:
        return await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")

    # تأكد من وجود رد على رسالة
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة العضو الذي تريد تقييده.")

    chat = await event.get_chat()

    # الشخص الذي تم الرد عليه
    user_to_restrict = await r.get_sender()

    # التحقق هل هو مشرف أو مالك
    try:
        participant = await ABH(GetParticipantRequest(
            channel=chat,
            participant=user_to_restrict.id
        ))
    except Exception as e:
        return await event.reply(f"❗ لم أتمكن من التحقق من صلاحيات الشخص: {e}")

    if isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
        return await event.reply("⚠️ لا يمكن تقييد المشرفين أو المالك.")

    thirty_minutes = int(time.time()) + 30 * 60

    rights = ChatBannedRights(
        until_date=thirty_minutes,
        send_messages=True
    )

    try:
        await ABH(EditBannedRequest(
            channel=chat,
            participant=user_to_restrict.id,
            banned_rights=rights
        ))
        await event.reply(f"✅ تم تقييد {user_to_restrict.first_name} من إرسال الرسائل.")
    except Exception as e:
        await event.reply(f"❌ فشل التقييد: {e}")

ABH.run_until_disconnected()
