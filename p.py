from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
import os

api_id = int(os.environ.get('API_ID'))  # تحويل api_id إلى int
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='^تقييد عام$'))
async def start(event):
    if not event.is_group:
        return await event.reply("هذا الأمر يعمل فقط في المجموعات.")

    sender = await event.get_sender()
    chat = await event.get_chat()

    try:
        participant = await ABH(GetParticipantRequest(
            channel=chat.id,
            user_id=sender.id
        ))
    except Exception as e:
        return await event.reply(f"لم أتمكن من الحصول على صلاحياتك.\nالخطأ: {e}")

    if isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
        await event.reply("⚠️ أنت مشرف أو مالك، لا يمكنك تنفيذ هذا الأمر.")
        return

    await event.reply("✅ أنت لست مشرفاً ولا مالكاً، يمكن تنفيذ الأمر.")

ABH.run_until_disconnected()
