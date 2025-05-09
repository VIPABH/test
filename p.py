from telethon import TelegramClient, events, Button
import uuid
import json
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
client = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# ملفات JSON
whispers_file = 'whispers.json'
sent_log_file = 'sent_whispers.json'

# تحميل بيانات الهمسات
if os.path.exists(whispers_file):
    try:
        with open(whispers_file, 'r') as f:
            whisper_links = json.load(f)
    except json.JSONDecodeError:
        whisper_links = {}
else:
    whisper_links = {}

# تحميل سجل الرسائل المرسلة
if os.path.exists(sent_log_file):
    try:
        with open(sent_log_file, 'r') as f:
            sent_whispers = json.load(f)
    except json.JSONDecodeError:
        sent_whispers = []
else:
    sent_whispers = []

# حفظ الملفات
def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f)

def save_sent_log():
    with open(sent_log_file, 'w') as f:
        json.dump(sent_whispers, f, ensure_ascii=False, indent=2)

# الجلسات
user_sessions = {}

@client.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.respond("❗ يجب الرد على رسالة الشخص الذي تريد أن تهمس له.")
        return

    whisper_id = str(uuid.uuid4())[:6]
    whisper_links[whisper_id] = {
        "from": event.sender_id,
        "to": reply.sender_id
    }
    save_whispers()

    button = Button.url("اضغط هنا لكتابة همستك", url=f"https://t.me/ytwibot?start={whisper_id}")
    await event.respond("✅ اضغط الزر لكتابة همستك الآن:", buttons=[button])

@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    if whisper_id in whisper_links:
        user_sessions[event.sender_id] = whisper_id
        await event.respond("✉️ تم فتح الجلسة! الآن يمكنك كتابة همستك (نص، صورة، فيديو، أي شيء).")
    else:
        await event.respond("⚠️ الرابط غير صالح أو انتهت صلاحيته.")

@client.on(events.NewMessage)
async def forward_whisper(event):
    if not event.is_private or (event.text and event.text.startswith('/')):
        return

    sender_id = event.sender_id
    whisper_id = user_sessions.get(sender_id)

    if whisper_id:
        data = whisper_links.get(whisper_id)
        if data:
            await client.forward_messages(data["to"], event.message)
            await event.respond("✅ تم إرسال همستك.")

            # حفظ المعلومات في JSON
            entry = {
                "event_id": event.id,
                "sender_id": sender_id,
                "whisper_id": whisper_id
            }
            sent_whispers.append(entry)
            save_sent_log()

            # حذف الجلسة والبيانات
            del user_sessions[sender_id]
            whisper_links.pop(whisper_id, None)
            save_whispers()

client.run_until_disconnected()
