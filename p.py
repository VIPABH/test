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
    if event.is_group:
        uid = event.sender.first_name
        unm = event.sender_id
        guid = event.chat_id
        if unm not in uinfo:
            uinfo[unm] = {}
        if guid not in uinfo[unm]:
            uinfo[unm][guid] = {"guid": guid, "unm": unm, "fname": uid, "msg": 1}
        else:
            uinfo[unm][guid]["msg"] += 1
@ABH.on(events.NewMessage(pattern='توب'))
async def show_res(event):
    await asyncio.sleep(2)
    uid = event.sender.first_name
    unm = event.sender_id
    guid = event.chat_id
    if unm in uinfo and guid in uinfo[unm]:
        msg_count = uinfo[unm][guid]["msg"]
        await event.reply(f"المستخدم [{unm}](tg://user?id={uid}) أرسل {msg_count} رسالة في هذه المجموعة.")
@ABH.on(events.NewMessage(pattern='رسائله|رسائلة|رسائل|الرسائل'))
async def show_res(event):
    await asyncio.sleep(2)
    r = await event.get_reply_message()
    uid = r.sender.first_name
    unm = r.sender_id
    guid = event.chat_id
    if unm in uinfo and guid in uinfo[unm]:
        msg_count = uinfo[unm][guid]["msg"]
        await event.reply(f"المستخدم [{unm}](tg://user?id={uid}) أرسل {msg_count} رسالة في هذه المجموعة.")

ABH.run_until_disconnected()
