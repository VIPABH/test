import random, os
from telethon import TelegramClient, events
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
points = {}
@ABH.on(events.NewMessage)
async def p(event):
    global uid, nid , gid 
    uid = event.sender_id
    nid = event.sender.username
    gid = event.chat_id
    points = {'uid': uid, "nid": nid, "gid": gid, "points": 0}
    points["points"] += 2
ABH.run_until_disconnected()
