import os, json
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator

# إعدادات الاتصال
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

AUTH_FILE = 'authorized_users.json'
if not os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, 'w') as f:
        json.dump({'معاون': []}, f)

def load_auth():
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def save_auth(data):
    with open(AUTH_FILE, 'w') as f:
        json.dump(data, f)

async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False

@ABH.on(events.NewMessage(pattern=r'^/اضافة معاون$'))
async def add_assistant(event):
    if not event.is_group:
        return
    if not await is_owner(event.chat_id, event.sender_id):
        return await event.reply("❌ هذا الأمر مخصص للمالك فقط.")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("❗ يجب الرد على رسالة المستخدم الذي تريد إضافته.")
    user_id = reply.sender_id
    data = load_auth()
    if user_id not in data['معاون']:
        data['معاون'].append(user_id)
        save_auth(data)
        await event.reply("✅ تم إضافة المستخدم إلى قائمة المعاونين.")
    else:
        await event.reply("ℹ️ المستخدم موجود بالفعل في قائمة المعاونين.")

@ABH.on(events.NewMessage(pattern=r'^/حذف معاون$'))
async def remove_assistant(event):
    if not event.is_group:
        return
    if not await is_owner(event.chat_id, event.sender_id):
        return await event.reply("❌ هذا الأمر مخصص للمالك فقط.")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("❗ يجب الرد على رسالة المستخدم الذي تريد حذفه.")
    user_id = reply.sender_id
    data = load_auth()
    if user_id in data['معاون']:
        data['معاون'].remove(user_id)
        save_auth(data)
        await event.reply("✅ تم حذف المستخدم من قائمة المعاونين.")
    else:
        await event.reply("ℹ️ المستخدم غير موجود في قائمة المعاونين.")

@ABH.on(events.NewMessage(pattern='^/القائمة$'))
async def show_list(event):
    if not event.is_group:
        return
    data = load_auth()
    msg = "**📋 قائمة المعاونين:**\n\n"
    if data["معاون"]:
        for user_id in data["معاون"]:
            msg += f"• [{user_id}](tg://user?id={user_id})\n"
    else:
        msg += "لا يوجد معاونين حالياً.\n"
    await event.reply(msg, parse_mode="md")
ABH.run_until_disconnected()
