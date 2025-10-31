from telethon import TelegramClient, events
from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    DiscardGroupCallRequest,
    EditGroupCallParticipantRequest,
    GetGroupCallRequest
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputGroupCall, InputPeerChannel
from ABH import ABH as client

# ──────────────────────────────
# 🔹 دالة مساعده للحصول على الاتصال الحالي
async def get_call(chat):
    full = await client(GetFullChannelRequest(chat))
    return full.full_chat.call

# ──────────────────────────────
# 🔸 فتح الاتصال
@client.on(events.NewMessage(pattern=r'^/فتح_اتصال$'))
async def open_call(event):
    chat = await event.get_input_chat()
    try:
        await client(CreateGroupCallRequest(peer=chat, random_id=0))
        await event.reply("✅ تم فتح الاتصال الصوتي بنجاح.")
    except Exception as e:
        await event.reply(f"❌ فشل فتح الاتصال:\n`{e}`")

# ──────────────────────────────
# 🔸 غلق الاتصال
@client.on(events.NewMessage(pattern=r'^/اغلاق_اتصال$'))
async def close_call(event):
    chat = await event.get_input_chat()
    try:
        call = await get_call(chat)
        if not call:
            return await event.reply("❌ لا يوجد اتصال نشط.")
        await client(DiscardGroupCallRequest(call=InputGroupCall(id=call.id, access_hash=call.access_hash)))
        await event.reply("🔒 تم إغلاق الاتصال الصوتي.")
    except Exception as e:
        await event.reply(f"❌ خطأ أثناء الغلق:\n`{e}`")

# ──────────────────────────────
# 🔇 كتم عضو
@client.on(events.NewMessage(pattern=r'^/كتم (\d+)$'))
async def mute_user(event):
    user_id = int(event.pattern_match.group(1))
    chat = await event.get_input_chat()
    call = await get_call(chat)
    if not call:
        return await event.reply("❌ لا يوجد اتصال نشط.")
    try:
        await client(EditGroupCallParticipantRequest(
            call=InputGroupCall(id=call.id, access_hash=call.access_hash),
            participant=user_id,
            muted=True
        ))
        await event.reply(f"🔇 تم كتم المستخدم `{user_id}`.")
    except Exception as e:
        await event.reply(f"❌ خطأ:\n`{e}`")

# ──────────────────────────────
# 🔊 رفع الكتم
@client.on(events.NewMessage(pattern=r'^/رفع_كتم (\d+)$'))
async def unmute_user(event):
    user_id = int(event.pattern_match.group(1))
    chat = await event.get_input_chat()
    call = await get_call(chat)
    if not call:
        return await event.reply("❌ لا يوجد اتصال نشط.")
    try:
        await client(EditGroupCallParticipantRequest(
            call=InputGroupCall(id=call.id, access_hash=call.access_hash),
            participant=user_id,
            muted=False
        ))
        await event.reply(f"🔊 تم رفع الكتم عن `{user_id}`.")
    except Exception as e:
        await event.reply(f"❌ خطأ:\n`{e}`")

# ──────────────────────────────
# 🔈 تعيين مستوى الصوت
@client.on(events.NewMessage(pattern=r'^/صوت (\d+) (\d+)$'))
async def set_volume(event):
    user_id = int(event.pattern_match.group(1))
    volume = int(event.pattern_match.group(2))
    chat = await event.get_input_chat()
    call = await get_call(chat)
    if not call:
        return await event.reply("❌ لا يوجد اتصال نشط.")
    if volume < 0 or volume > 200:
        return await event.reply("⚠️ مستوى الصوت يجب أن يكون بين 0 و 200.")
    try:
        await client(EditGroupCallParticipantRequest(
            call=InputGroupCall(id=call.id, access_hash=call.access_hash),
            participant=user_id,
            volume=volume
        ))
        await event.reply(f"🔉 تم تعيين مستوى الصوت للمستخدم `{user_id}` إلى `{volume}`.")
    except Exception as e:
        await event.reply(f"❌ خطأ:\n`{e}`")

# ──────────────────────────────
print("🚀 تم تشغيل البوت، بانتظار الأوامر...")
