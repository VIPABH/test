from telethon import TelegramClient, events
import os, asyncio

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)

uinfo = {}

@ABH.on(events.NewMessage)
async def msgs(event):
    global uinfo
    uid = event.sender.first_name
    unm = event.sender_id    
    if unm not in uinfo:
        uinfo[unm] = {"unm": unm, "fname": uid, "msg": 1}
    else:
        uinfo[unm]["msg"] += 1
@ABH.on(events.NewMessage(pattern='توب'))
async def show_res(event):
    uid = event.sender.first_name
    unm = event.sender_id
    await event.reply(f"User: {uid} ({unm}) has sent {uinfo[unm]['msg']} messages.")
ABH.run_until_disconnected()
