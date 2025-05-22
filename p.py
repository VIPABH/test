from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest, EditBannedRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin, ChatBannedRights
import os, time

# إعدادات الاتصال
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# قاعدة بيانات مؤقتة في الذاكرة لحفظ وقت التقييد
restriction_times = {}

# أمر التقييد العام
@ABH.on(events.NewMessage(pattern='^تقييد عام$'))
async def restrict_user(event):
    if not event.is_group:
        return await event.reply("❗ هذا الأمر يعمل فقط في المجموعات.")
    
    r = await event.get_reply_message()
    if not r:
        return await event.reply("❗ يجب الرد على رسالة العضو الذي تريد تقييده.")    
    
    chat = await event.get_chat()
    sender = await r.get_sender()
    try:
        participant = await ABH(GetParticipantRequest(channel=chat.id, participant=sender.id))
        if isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
            return await event.reply("⚠️ أنت مشرف أو مالك، لا يمكنك استخدام هذا الأمر.")
    except:
        return await event.reply("❗ لم أتمكن من التحقق من صلاحياتك.")    
    user_to_restrict = await r.get_sender()
    user_id = user_to_restrict.id
    restriction_times[user_id] = int(time.time())
    
    rights = ChatBannedRights(
        until_date=int(time.time()) + 1800,
        send_messages=True
    )
    try:
        await ABH(EditBannedRequest(channel=chat.id, participant=user_id, banned_rights=rights))
        await event.reply(f"✅ تم تقييد {user_to_restrict.first_name} لمدة 30 دقيقة.")
    except Exception as e:
        await event.reply(f"❌ فشل التقييد: {e}")
@ABH.on(events.NewMessage)
async def monitor_messages(event):
    if not event.is_group:
        return
    user_id = event.sender_id
    now = int(time.time())
    if user_id in restriction_times:
        elapsed = now - restriction_times[user_id]
        if elapsed < 600:
            try:
                chat = await event.get_chat()
                rights = ChatBannedRights(
                    until_date=now + 1800,
                    send_messages=True
                )
                await ABH(EditBannedRequest(channel=chat.id, participant=user_id, banned_rights=rights))
                restriction_times[user_id] = now
                await event.reply("⛔ لا يمكنك إرسال الرسائل بعد، تم إعادة تقييدك لمدة 30 دقيقة.")
            except:
                pass
ABH.run_until_disconnected()
