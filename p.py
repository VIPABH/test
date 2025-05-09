from telethon import TelegramClient, events, Button
import uuid
import json
import os

# إعدادات العميل
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
client = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

# ملفات التخزين
whispers_file = 'whispers.json'
sent_log_file = 'sent_whispers.json'

# تحميل البيانات من الملفات إذا كانت موجودة
if os.path.exists(whispers_file):
    try:
        with open(whispers_file, 'r') as f:
            whisper_links = json.load(f)
    except json.JSONDecodeError:
        whisper_links = {}
else:
    whisper_links = {}

if os.path.exists(sent_log_file):
    try:
        with open(sent_log_file, 'r') as f:
            sent_whispers = json.load(f)
    except json.JSONDecodeError:
        sent_whispers = []
else:
    sent_whispers = []

# حفظ البيانات إلى الملفات
def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f, ensure_ascii=False, indent=2)

def save_sent_log():
    with open(sent_log_file, 'w') as f:
        json.dump(sent_whispers, f, ensure_ascii=False, indent=2)

# متغيرات المستخدم
user_sessions = {}
user_targets = {}

# التعامل مع همسة جديدة
@client.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.respond("❗ يجب الرد على رسالة الشخص الذي تريد أن تهمس له.")
        return

    whisper_id = str(uuid.uuid4())[:6]  # توليد معرف UUID فريد
    whisper_links[whisper_id] = {
        "from": event.sender_id,
        "to": reply.sender_id,
        "chat_id": event.chat_id,
        "text": "نص الهمسة هنا"  # يمكنك تخصيص النص هنا
    }
    save_whispers()

    # تخزين البيانات الإضافية (مثل الاسم)
    from_user = await event.get_sender()
    to_user = await reply.get_sender()
    user_targets[whisper_id] = {"name": to_user.first_name}

    # إضافة زر للمستخدم لفتح الرابط
    button = Button.url("اضغط هنا لإرسال همستك", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await event.respond(f"📢 هناك همسة جديدة:\n👤 من: {from_user.first_name}\n👤 إلى: {to_user.first_name}\n\n↘️ اضغط على الزر لبدء إرسال همستك:", buttons=[button])

# بدء جلسة باستخدام الرابط
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)

    # طباعة البيانات المسترجعة للـ debug
    print(f"تم استرجاع whisper_id: {whisper_id}")
    print(f"البيانات المسترجعة: {data}")

    if data:
        user_sessions[event.sender_id] = whisper_id
        target_name = user_targets.get(whisper_id, {}).get("name", "الشخص")
        sender = await event.get_sender()

        # التحقق إذا كانت هناك همسة مخزنة (نص أو وسائط)
        if 'text' in data:
            await event.respond(f"✉️ أهلاً {sender.first_name}، إليك الهمسة التالية لإرسالها إلى {target_name}:\n\n{data['text']}")
        else:
            await event.respond(f"✉️ أهلاً {sender.first_name}، أرسل الآن همستك إلى {target_name}.")
    else:
        await event.respond("⚠️ الرابط غير صالح أو انتهت صلاحيته.")

# التعامل مع إرسال الهمسات
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

    v = event.message
    b = Button.url(">", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await client.send_message(data['chat_id'], 'همسة جديدة', buttons=[b])
    await client.forward_messages(data["to"], v)
    await event.respond("✅ تم إرسال همستك بنجاح.")

    # تخزين البيانات في السجل
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })

    await asyncio.sleep(5)
    save_sent_log()

    # تنظيف الجلسات والبيانات بعد الإرسال
    user_sessions.pop(sender_id, None)
    whisper_links.pop(whisper_id, None)
    user_targets.pop(whisper_id, None)
    save_whispers()

# تشغيل العميل
client.run_until_disconnected()
