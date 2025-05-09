from telethon import TelegramClient, events, Button
import uuid
import json
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

whispers_file = 'whispers.json'
pending_media_file = 'pending_media.json'

# تحميل روابط الهمسات
if os.path.exists(whispers_file):
    with open(whispers_file, 'r') as f:
        whisper_links = json.load(f)
else:
    whisper_links = {}

# تحميل قائمة الوسائط المؤجلة
if os.path.exists(pending_media_file):
    with open(pending_media_file, 'r') as f:
        pending_media = json.load(f)
else:
    pending_media = {}

def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f)

def save_pending_media():
    with open(pending_media_file, 'w') as f:
        json.dump(pending_media, f)

user_sessions = {}

# أمر اهمس (في مجموعة)
@client.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.respond("❗ يجب الرد على رسالة الشخص الذي تريد أن تهمس له.")
        return

    whisper_id = str(uuid.uuid4())[:6]

    whisper_links[whisper_id] = {
        "from": event.sender_id,
        "to": reply.sender_id,
        "chat_id": event.chat_id
    }
    save_whispers()

    from_user = await event.get_sender()
    to_user = await reply.get_sender()

    button = Button.url("✉️ اضغط لقراءة الهمسة", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await client.send_message(
        event.chat_id,
        f"📨 تم إرسال همسة ميديا من **{from_user.first_name}** إلى **{to_user.first_name}**.",
        buttons=[button]
    )

# استقبال الضغط على الزر (start uuid)
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if data and event.sender_id == data['to']:
        user_sessions[event.sender_id] = whisper_id
        await event.respond("✉️ تم فتح الجلسة. أرسل همستك الآن (نص أو ميديا).")

        # إذا كانت هناك ميديا مؤجلة لهذا uuid، أرسلها الآن
        if whisper_id in pending_media:
            media_msg = pending_media[whisper_id]
            await client.send_file(event.sender_id, media_msg['file_id'], caption=media_msg.get("caption", ""))
            del pending_media[whisper_id]
            save_pending_media()

            # حذف الجلسة
            user_sessions.pop(event.sender_id, None)
            whisper_links.pop(whisper_id, None)
            save_whispers()
    else:
        await event.respond("⚠️ الرابط غير صالح أو لا يمكنك استخدامه.")

# استقبال الهمسة (نص أو ميديا)
@client.on(events.NewMessage)
async def forward_whisper(event):
    if not event.is_private or (event.text and event.text.startswith('/')):
        return

    sender_id = event.sender_id
    whisper_id = user_sessions.get(sender_id)
    if not whisper_id:
        return

    data = whisper_links.get(whisper_id)
    if not data:
        return

    # إرسال ميديا أو نص
    if event.media:
        # تخزين الوسائط مؤقتًا ليرسلها لاحقًا
        msg = await event.respond("✅ تم استلام الوسائط، انتظر الضغط على الزر...")
        file_id = event.file.id if hasattr(event.file, 'id') else None

        if file_id:
            pending_media[whisper_id] = {
                "file_id": file_id,
                "caption": event.text or ""
            }
            save_pending_media()
            await event.respond("✅ الوسائط محفوظة، سيتم إرسالها عند ضغط الزر.")
        else:
            await event.respond("⚠️ لم يتم التعرف على الوسائط.")
    else:
        # نص عادي
        await client.send_message(data["to"], event.message.message)
        await event.respond("✅ تم إرسال همستك النصية.")

        # حذف الجلسة
        user_sessions.pop(sender_id, None)
        whisper_links.pop(whisper_id, None)
        save_whispers()
client.run_until_disconnected()
