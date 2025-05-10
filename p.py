from telethon import TelegramClient, events, Button
import uuid
import json
import os
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
        await event.respond("يجب الرد على رسالة الشخص الذي تريد أن تهمس له.")
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
    button = Button.url("اضغط هنا للبدء", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await event.respond(
        f'همسة مرسله من {from_user.first_name} الى {to_user.first_name}',
        buttons=[button]
    )
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if not data:
        await event.respond(" الهمسة غير موجوده في التخزين😔")
        return
    if event.sender_id != data['to'] and event.sender_id != data['from']:
        await event.respond("ماتكدر تشوف الهمسه💔")
        return
    sender = await event.get_sender()
    if 'media' in data:
        media_data = data['media']
        try:
            await client.send_file(
                event.sender_id,
                media_data['file_id'],
                caption=media_data.get("caption", ""),
                protect_content=True
            )
        except Exception:
            await event.respond(" حدث خطأ أثناء إرسال الهمسة.")
    elif 'text' in data:
            await event.respond(data['text'])
    else:
        await event.respond(f" أهلاً {sender.first_name}، ارسل كلام الهمسة او ميديا.")
    user_sessions[event.sender_id] = whisper_id
@client.on(events.NewMessage)
async def forward_whisper(event):
    global l
    l = False
    if not event.is_private or l:
        return
    sender_id = event.sender_id
    whisper_id = user_sessions.get(sender_id)
    if not whisper_id:
        return
    data = whisper_links.get(whisper_id)
    if not data:
        return
    l = True
    msg = event.message
    b = Button.url("فتح الهمسة", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    data = whisper_links.get(whisper_id)
    from_name = data.get("from_name", "مجهول")
    to_name = data.get("to_name", "مجهول")
    await client.send_message(
        data['chat_id'],
        f'همسة مرسله من ( {from_name} ) الى ( {to_name} )',
        buttons = [b]
    )
    if msg.media:
        whisper_links[whisper_id]['media'] = {
            'file_id': msg.file.id,
            'caption': msg.text or ""
        }
    elif msg.text:
        whisper_links[whisper_id]['text'] = msg.text
    save_whispers()
    if msg.media:
        media_data = whisper_links[whisper_id]['media']
        await client.send_file(event.sender_id, media_data['file_id'], caption=media_data.get("caption", ""), protect_content=True)
    else:
        await event.respond("تم ارسال الهمسة")
        l = False
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })
    save_sent_log()
client.run_until_disconnected()
