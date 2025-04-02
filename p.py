import os
import json
from telethon import TelegramClient, events
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
def load_points(filename="rose.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
rose = load_points()
def add_points(uid, gid, nid, rose):
    uid, gid, nid = str(uid), str(gid), str(nid)
    if gid not in rose:
        rose[gid] = {}
    if uid not in rose[gid]:
        rose[gid][uid] = {"name": nid, "count": 1}
    else:
        rose[gid][uid]["count"]
    save_points(rose)

@ABH.on(events.NewMessage(pattern=r'رفع وردة\s+(\d+)'))
async def rose_handler(event):
    number = int(event.pattern_match.group(1))
    if not number:
        await event.reply('بشكد تشتري الورده؟')
    message = await event.get_reply_message()
    if not message or not message.sender:
        await event.reply("يجب الرد على رسالة شخص لرفعه الوردة!")
        return
    uid = message.sender_id
    nid = message.sender.first_name or "مجهول"
    chat = str(event.chat_id)
    add_points(uid, chat, nid, rose)
    if rose[uid][nid][chat] > number:
        await event.reply(f"✅ تم رفع الوردة لـ {nid} 🌹")
    else:
        await event.reply('يا فقير ماعندك فلوس حته ترفع')

@ABH.on(events.NewMessage(pattern='الوراريد'))
async def show_handler(event):
    chat_id = str(event.chat_id)
    if chat_id not in rose or not rose[chat_id]:
        await event.reply("🚫 لا يوجد أي ورود في هذه المجموعة حتى الآن.")
        return
    response = f"🌹 قائمة الورود في هذه المجموعة ({chat_id}) 🌹\n"
    for uid, data in rose[chat_id].items():
        response += f"👤 {data['name']}: {data['count']} وردة\n"
    await event.reply(response)
ABH.run_until_disconnected()
