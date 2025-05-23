import os, json
from telethon import TelegramClient, events
from Resources import mention
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)
import os
import json
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator

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

def is_assistant(user_id):
    data = load_auth()
    return user_id in data.get('معاون', [])

async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False

async def mention(event, user):
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"[{name}](tg://user?id={user.id})"

@ABH.on(events.NewMessage(pattern=r'^رفع معاون$'))
async def add_assistant(event):
    if not event.is_group:
        return
    s = await event.get_sender()
    sm = await mention(event, s)
    chat_id = event.chat_id
    user_id = event.sender_id
    if not (await is_owner(chat_id, user_id) or user_id == 1910015590):
        return await event.reply(f"عذراً {sm}، هذا الأمر مخصص للمالك فقط.")
    
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply(f"عزيزي {sm}، يجب الرد على رسالة المستخدم الذي تريد إضافته.")
    
    target_id = reply.sender_id
    data = load_auth()
    if target_id not in data['معاون']:
        data['معاون'].append(target_id)
        save_auth(data)
        sender = await reply.get_sender()
        rm = await mention(event, sender)
        await event.reply(f"✅ تم رفع المستخدم {rm} إلى معاون.")
    else:
        await event.reply(f"ℹ️ {sm}، المستخدم موجود مسبقًا في قائمة المعاونين.")

@ABH.on(events.NewMessage(pattern=r'^تنزيل معاون$'))
async def remove_assistant(event):
    if not event.is_group:
        return
    s = await event.get_sender()
    sm = await mention(event, s)
    chat_id = event.chat_id
    user_id = event.sender_id
    if not (await is_owner(chat_id, user_id) and user_id == 1910015590):
        return await event.reply(f"عذرًا {sm}، هذا الأمر مخصص للمالك فقط.")

    reply = await event.get_reply_message()
    if not reply:
        return await event.reply(f"عزيزي {sm}، يجب الرد على رسالة المستخدم الذي تريد تنزيله.")
    
    target_id = reply.sender_id
    data = load_auth()
    target_user = await reply.get_sender()
    rm = await mention(event, target_user)
    if target_id in data['معاون']:
        data['معاون'].remove(target_id)
        save_auth(data)
        await event.reply(f"🗑️ تم إزالة {rm} من قائمة المعاونين.")
    else:
        await event.reply(f"⚠️ {rm} غير موجود في القائمة.")
@ABH.on(events.NewMessage(pattern='^المعاونين$'))
async def show_list(event):
    if not event.is_group:
        return
    data = load_auth()
    msg = "**📋 قائمة المعاونين:**\n\n"
    if data["معاون"]:
        for user_id in data["معاون"]:
            try:
                user = await ABH.get_entity(user_id)
                user_mention = await mention(event, user)
                msg += f"• {user_mention} ↔ `{user.id}`\n"
            except:
                msg += f"• معرف غير صالح: `{user_id}`\n"
    else:
        msg += "لا يوجد معاونين حالياً.\n"
    await event.reply(msg, parse_mode="md")
ABH.run_until_disconnected()
