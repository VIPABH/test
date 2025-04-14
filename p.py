from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='صلاحياتي'))
async def my_rights(event):
    try:
        chat = await event.get_input_chat()
        sender_id = event.sender_id
        result = await ABH(GetParticipantRequest(channel=chat, participant=sender_id))
        rights = result.participant.admin_rights
        perms = [k for k, v in rights.to_dict().items() if v] if rights else []
        await event.reply(f"صلاحياتك ↞ {'،'.join(perms) if perms else 'لا يوجد صلاحيات'}")
    except Exception:
        await event.reply("لا يمكن عرض الصلاحيات.")

@ABH.on(events.NewMessage(pattern='صلاحياته'))
async def his_rights(event):
    try:
        msg = await event.get_reply_message()
        if not msg:
            await event.reply("رد على رسالة المستخدم أولًا.")
            return
        chat = await event.get_input_chat()
        sender_id = msg.sender_id
        result = await ABH(GetParticipantRequest(channel=chat, participant=sender_id))
        rights = result.participant.admin_rights
        perms = [k for k, v in rights.to_dict().items() if v] if rights else []
        await event.reply(f"صلاحياته ↞ {'،'.join(perms) if perms else 'لا يوجد صلاحيات'}")
    except Exception:
        await event.reply("لا يمكن عرض الصلاحيات.")

ABH.start()
ABH.run_until_disconnected()
