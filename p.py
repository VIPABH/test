from telethon import TelegramClient, events, Button
import uuid
import json
import os

# بيانات الدخول من المتغيرات البيئية
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء العميل
client = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# ملفات التخزين
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

# تحميل سجل الإرسال
if os.path.exists(sent_log_file):
    try:
        with open(sent_log_file, 'r') as f:
            sent_whispers = json.load(f)
    except json.JSONDecodeError:
        sent_whispers = []
else:
    sent_whispers = []

# دوال الحفظ
def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f)

def save_sent_log():
    with open(sent_log_file, 'w') as f:
        json.dump(sent_whispers, f, ensure_ascii=False, indent=2)

# تخزين الجلسات المؤقتة
user_sessions = {}
user_targets = {}

# أمر اهمس
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

    # حفظ اسم المرسل إليه
    user_targets[whisper_id] = {
        "name": reply.sender.first_name
    }

    button = Button.url("اضغط هنا لكتابة همستك", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await event.respond("✅ اضغط للمتابعة", buttons=[button])

# عند الضغط على الرابط
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if data:
        user_sessions[event.sender_id] = whisper_id
        target_name = user_targets.get(whisper_id, {}).get("name", "الشخص")
        sender = await event.get_sender()
        await event.respond(f"✉️ أهلاً ({sender.first_name})، ارسل رسالتك لإرسالها إلى {target_name}.")
    else:
        await event.respond("⚠️ الرابط غير صالح أو انتهت صلاحيته.")

# استقبال الهمسة
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

    # إرسال الهمسة
    await client.forward_messages(data["to"], event.message)
    await event.respond("✅ تم إرسال همستك.")

    # تسجيل معلومات الهمسة
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })
    save_sent_log()

    # حذف الجلسة
    user_sessions.pop(sender_id, None)
    whisper_links.pop(whisper_id, None)
    user_targets.pop(whisper_id, None)
    save_whispers()
