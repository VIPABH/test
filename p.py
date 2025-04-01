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
    except FileNotFoundError:
        return {}
def save_points(data, filename="rose.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
rose = load_points()
def add_points(uid, gid, rose):
    uid, gid, nid = str(uid), str(gid), str(nid)
    if uid not in rose:
        rose[uid] = {}
    if gid not in rose[uid][nid]:
        rose[uid][gid][nid]
    rose[uid][gid][nid]
    save_points(rose)
@ABH.on(events.NewMessage(pattern='رفع وردة'))
async def rose(event):
    message = await event.get_reply_message()
    uid = message.sender_id
    nid = message.first_name
    chat = event.chat_id
    add_points(uid, nid, chat)
@ABH.on(events.NewMessage(pattern='الوراريد'))
async def show(event):
    for abh in rose:
        await event.reply(f'{abh}')
ABH.run_until_disconnected()
