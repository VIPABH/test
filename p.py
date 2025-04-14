from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
import logging, os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

logging.basicConfig(level=logging.INFO)

@ABH.on(events.NewMessage(pattern='لقبي'))
async def nickname(event):
    try:
        chat = await event.get_input_chat()
        sender_id = event.sender_id

        result = await ABH(GetParticipantRequest(
            channel=chat,
            participant=sender_id
        ))

        participant = result.participant
        nickname = getattr(participant, 'rank', None) or "لا يوجد لقب"
        await event.reply(f"لقبك ↞ {nickname}")

    except Exception as e:
        await event.reply("المستخدم ليس مشرفًا أو لا يمكن العثور عليه.")
        logging.error(f"لقبي Error: {str(e)}")

@ABH.on(events.NewMessage(pattern='لقبه'))
async def nickname_r(event):
    try:
        msg = await event.get_reply_message()
        if not msg:
            await event.reply("رد على رسالة المستخدم أولًا.")
            return

        chat = await event.get_input_chat()
        sender_id = msg.sender_id

        result = await ABH(GetParticipantRequest(
            channel=chat,
            participant=sender_id
        ))

        participant = result.participant
        nickname = getattr(participant, 'rank', None) or "لا يوجد لقب"
        await event.reply(f"لقبه ↞ {nickname}")

    except Exception as e:
        await event.reply("المستخدم ليس مشرفًا أو لا يمكن العثور عليه.")
        logging.error(f"لقبه Error: {str(e)}")

ABH.start()
ABH.run_until_disconnected()
