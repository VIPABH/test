from telethon import TelegramClient, events, Button
import uuid
import json
import os, asyncio
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
client = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
whispers_file = 'whispers.json'
sent_log_file = 'sent_whispers.json'
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
def save_whispers():
    with open(whispers_file, 'w') as f:
        json.dump(whisper_links, f)
def save_sent_log():
    with open(sent_log_file, 'w') as f:
        json.dump(sent_whispers, f, ensure_ascii=False, indent=2)
user_sessions = {}
user_targets = {}
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

    user_targets[whisper_id] = {
        "name": to_user.first_name
    }
    print(whisper_id)
    button = Button.url("✉️ اضغط هنا لإرسال همستك", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await event.respond(
        f"📢 هناك همسة جديدة:\n👤 من: {from_user.first_name}\n👤 إلى: {to_user.first_name}\n\n↘️ اضغط على الزر لبدء إرسال همستك:",
        buttons=[button]
    )
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)

    if not data:
        await event.respond("⚠️ الرابط غير صالح أو انتهت صلاحيته.")
        return

    # تسجيل الجلسة للمستخدم الحالي
    user_sessions[event.sender_id] = whisper_id

    # تحديد اسم المستقبل أو "الشخص"
    target_name = user_targets.get(whisper_id, {}).get("name", "الشخص")
    sender = await event.get_sender()

    # التحقق من وجود رسالة نصية محفوظة
    if 'text' in data:
        await event.respond(
            f"✉️ أهلاً {sender.first_name}، إليك الهمسة التالية لإرسالها إلى {target_name}:\n\n{data['text']}"
        )

    # التحقق من وجود ملف محفوظ
    elif 'media' in data:
        media_data = data['media']
        try:
            await client.send_file(
                event.sender_id,
                media_data['file_id'],
                caption=media_data.get("caption", "")
            )
            await event.respond(
                f"✉️ أهلاً {sender.first_name}، إليك الهمسة التالية لإرسالها إلى {target_name}."
            )
        except Exception as e:
            print(f"خطأ أثناء إرسال الملف: {e}")
            await event.respond("⚠️ حدث خطأ أثناء إرسال الهمسة.")
    else:
        # لا يوجد أي محتوى محفوظ، فقط فتح الجلسة
        await event.respond(
            f"✉️ أهلاً {sender.first_name}، أرسل الآن همستك إلى {target_name}."
        )
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

    msg = event.message
    button = Button.url("فتح الهمسة", url=f"https://t.me/Hauehshbot?start={whisper_id}")

    # إعلام القروب أو الدردشة أن هنالك همسة جديدة
    await client.send_message(
        data['chat_id'],
        f"📨 تم إرسال همسة جديدة من {event.sender.first_name}",
        buttons=[button]
    )

    # تخزين محتوى الرسالة حسب وجود ملف أو فقط نص
    if msg.media:  # إن كانت الرسالة تحتوي ملفًا (صورة، فيديو، صوت...)
        whisper_links[whisper_id]['media'] = {
            'file_id': msg.file.id,
            'caption': msg.text or ""
        }
    elif msg.text:  # فقط نص
        whisper_links[whisper_id]['text'] = msg.text

    save_whispers()  # حفظ التحديث في ملف JSON

    # توجيه الرسالة إلى الطرف الآخر
    await client.forward_messages(data["to"], msg)
    await event.respond("✅ تم إرسال همستك بنجاح.")

    # تسجيل الإرسال في سجل الإرسال
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })
    save_sent_log()
    user_sessions.pop(sender_id, None)
    whisper_links.pop(whisper_id, None)  # حذف الرابط فقط، دون حذف media/text
    user_targets.pop(whisper_id, None)
    save_whispers()
client.run_until_disconnected()
