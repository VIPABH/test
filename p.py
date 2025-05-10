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
l = {}
@client.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    global l, m1, reply
    sender_id = event.sender_id
    if sender_id in l and l[sender_id]:
        await event.reply("هيييي ماتكدر تسوي همستين بوقت واحد")
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("صديقي الامر هاذ ميشتغل اذا مو رد")
        return
    whisper_id = str(uuid.uuid4())[:6]
    from_user = await event.get_sender()
    to_user = await reply.get_sender()
    whisper_links[whisper_id] = {
        "from": sender_id,
        "to": reply.sender_id,
        "chat_id": event.chat_id,
        "from_name": from_user.first_name,
        "to_name": to_user.first_name
    }
    save_whispers()
    button = Button.url("اضغط هنا للبدء", url=f"https://t.me/{(await client.get_me()).username}?start={whisper_id}")
    m1 = await event.reply(
        f'همسة مرسلة من {from_user.first_name} إلى {to_user.first_name}',
        buttons=[button]
    )
    l[sender_id] = True
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    if not data:
        await event.reply("الهمسة غير موجودة في التخزين.")
        return
    if event.sender_id != data['to'] and event.sender_id != data['from']:
        await event.reply("لا يمكنك مشاهدة هذه الهمسة.")
        return
    sender = await event.get_sender()
    if 'original_msg_id' in data and 'from_user_chat_id' in data:
        await client.forward_messages(
            event.sender_id,
            messages=data['original_msg_id'],
            from_peer=data['from_user_chat_id']
        )
    elif 'text' in data:
        await event.reply(data['text'])
    else:
        await event.reply(f"أهلاً {sender.first_name}، ارسل نص الهمسة أو ميديا.")
    user_sessions[event.sender_id] = whisper_id
@client.on(events.NewMessage(incoming=True))
async def forward_whisper(event):
    global l, m2
    if not event.is_private or (event.text and event.text.startswith('/')):
        return
    sender_id = event.sender_id
    if sender_id not in l or not l[sender_id]:
        return
    whisper_id = user_sessions.get(sender_id)
    if not whisper_id:
        return
    data = whisper_links.get(whisper_id)
    if not data:
        return
    msg = event.message
    b = Button.url("فتح الهمسة", url=f"https://t.me/{(await client.get_me()).username}?start={whisper_id}")
    from_name = data.get("from_name", "مجهول")
    to_name = data.get("to_name", "مجهول")
    await m1.delete()
    m2 = await client.send_message(
        data['chat_id'],
        f'همسة مرسلة من ({from_name}) إلى ({to_name})',
        buttons=[b], reply_to=reply)
    if msg.media:
        whisper_links[whisper_id]['original_msg_id'] = msg.id
        whisper_links[whisper_id]['from_user_chat_id'] = sender_id
    elif msg.text:
        whisper_links[whisper_id]['text'] = msg.text
    save_whispers()
    if msg.media:
        await event.reply("تم إرسال همسة ميديا بنجاح.")
    else:
        await event.reply("تم إرسال همسة بنجاح.")
    sender = await event.get_sender()
    sent_whispers.append({
        "event_id": event.id,
        "sender_id": sender.id,
        "sender_name": sender.first_name,
        "to_id": data["to"],
        "uuid": whisper_id
    })
    save_sent_log()
    l[sender_id] = False
client.run_until_disconnected()
