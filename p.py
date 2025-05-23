from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator
import os, json

# إعدادات الاتصال
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session', api_id, api_hash).start(bot_token=bot_token)

# قاعدة بيانات للمعاونين والمنظمين
AUTH_FILE = 'authorized_users.json'
if not os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, 'w') as f:
        json.dump({'معاون': [], 'منظم': []}, f)

def load_auth():
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def save_auth(data):
    with open(AUTH_FILE, 'w') as f:
        json.dump(data, f)

# التحقق من أن المرسل هو المالك
async def is_owner(chat_id, user_id):
    try:
        participant = await ABH(GetParticipantRequest(channel=chat_id, participant=user_id))
        return isinstance(participant.participant, ChannelParticipantCreator)
    except:
        return False

# إضافة معاون أو منظم
@ABH.on(events.NewMessage(pattern=r'^(/اضافة معاون|/اضافة منظم)$'))
async def add_role(event):
    if not event.is_group:
        return
    role = 'معاون' if 'معاون' in event.raw_text else 'منظم'
    if not await is_owner(event.chat_id, event.sender_id):
        return await event.reply("❌ هذا الأمر مخصص للمالك فقط.")
    
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("❗ يجب الرد على رسالة المستخدم الذي تريد إضافته.")

    user_id = reply.sender_id
    data = load_auth()
    if user_id not in data[role]:
        data[role].append(user_id)
        save_auth(data)
        await event.reply(f"✅ تم إضافة المستخدم إلى قائمة {role}.")
    else:
        await event.reply(f"ℹ️ المستخدم موجود بالفعل في قائمة {role}.")

# حذف معاون أو منظم
@ABH.on(events.NewMessage(pattern=r'^(/حذف معاون|/حذف منظم)$'))
async def remove_role(event):
    if not event.is_group:
        return
    role = 'معاون' if 'معاون' in event.raw_text else 'منظم'
    if not await is_owner(event.chat_id, event.sender_id):
        return await event.reply("❌ هذا الأمر مخصص للمالك فقط.")

    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("❗ يجب الرد على رسالة المستخدم الذي تريد حذفه.")

    user_id = reply.sender_id
    data = load_auth()
    if user_id in data[role]:
        data[role].remove(user_id)
        save_auth(data)
        await event.reply(f"✅ تم حذف المستخدم من قائمة {role}.")
    else:
        await event.reply(f"ℹ️ المستخدم غير موجود في قائمة {role}.")

# عرض القوائم
@ABH.on(events.NewMessage(pattern='^/القائمة$'))
async def show_list(event):
    if not event.is_group:
        return

    data = load_auth()
    msg = "**📋 القائمة الحالية:**\n\n"

    if data["معاون"]:
        msg += "**👤 المعاونين:**\n"
        for user_id in data["معاون"]:
            msg += f"• [{user_id}](tg://user?id={user_id})\n"
    else:
        msg += "**👤 المعاونين:** لا يوجد\n"

    if data["منظم"]:
        msg += "\n**🛠️ المنظمين:**\n"
        for user_id in data["منظم"]:
            msg += f"• [{user_id}](tg://user?id={user_id})\n"
    else:
        msg += "\n**🛠️ المنظمين:** لا يوجد\n"

    await event.reply(msg, parse_mode="md")

# تشغيل البوت
ABH.run_until_disconnected()
