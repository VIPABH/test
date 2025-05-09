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
@client.on(events.NewMessage(pattern='اهمس'))
async def handle_whisper(event):
    global chat, t, w, x, t
    x = await event.get_sender() 
    chat = event.chat_id
    reply = await event.get_reply_message()
    t = reply.first_name
    if not reply:
        await event.respond("يجب الرد على رسالة الشخص الذي تريد أن تهمس له.")
        return
    whisper_id = str(uuid.uuid4())[:6]
    whisper_links[whisper_id] = {
        "from": event.sender_id,
        "to": reply.sender_id
    }
    save_whispers()
    w = whisper_id
    button = Button.url("اضغط هنا لكتابة همستك", url=f"https://t.me/Hauehshbot?start={whisper_id}")
    await event.respond("اضغط للمتابعة", buttons=[button])
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def start_with_param(event):
    whisper_id = event.pattern_match.group(1)
    if whisper_id in whisper_links:
        user_sessions[event.sender_id] = whisper_id
        x = event.sender.first_name
        await event.respond(f"اهلا ( {x} ) ارسل رسالة ل ارسالها ل {t}")
    else:
        await event.respond("الرابط غير صالح أو انتهت صلاحيته.")
@client.on(events.NewMessage)
async def forward_whisper(event):
    if not event.is_private or (event.text and event.text.startswith('/')):
        return
    sender_id = event.sender_id
    whisper_id = user_sessions.get(sender_id)
    if whisper_id:
        data = whisper_links.get(whisper_id)
        if data:
            button = Button.url("اضغط هنا لكتابة همستك", url=f"https://t.me/Hauehshbot?start={whisper_id}")
            await client.send_message(chat, f'همسه مديا مرسلة من ( {x.first_name} ) الى ( {t.first_name} )', buttons=[button])
            await event.respond("تم إرسال همستك.")
@client.on(events.NewMessage(pattern=r'/start (\w+)'))
async def t(event):
    whisper_id = event.pattern_match.group(1)
    data = whisper_links.get(whisper_id)
    await client.forward_messages(data["to"], event.message)

client.run_until_disconnected()
