from telethon import TelegramClient, events
import os, asyncio, time

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
    guid = event.chat_id
    unm = event.sender_id
    sorted_users = sorted(uinfo.items(), key=lambda x: x[1][guid]['msg'], reverse=True)[:15]
    top_users = []
    for user, data in sorted_users:
        if guid in data:
            top_users.append(f"{data[guid][unm]['msg']} رسائل")
    if top_users:
        await event.reply("\n".join(top_users))
    else:
        await event.reply("لا توجد بيانات لعرضها.")
@ABH.on(events.NewMessage(pattern='رسائلي'))
async def show_res(event):
    r = await event.get_reply_message()
    await asyncio.sleep(2)
    if not r:
        return
    uid1 = event.sender.first_name
    unm1 = event.sender_id
    guid1 = event.chat_id
    if unm1 in uinfo and guid1 in uinfo[unm1]:
        msg_count = uinfo[unm1][guid1]["msg"]
        await event.reply(f"المستخدم [{uid1}](tg://user?id={unm1}) ارسلت {msg_count} رسالة في هذه المجموعة.")
@ABH.on(events.NewMessage(pattern='رسائله|رسائلة|رسائل|الرسائل'))
async def show_res(event):
    r = await event.get_reply_message()
    await asyncio.sleep(2)
    if not r:
        return
    uid1 = r.sender.first_name
    unm1 = r.sender_id
    guid1 = event.chat_id
    if unm1 in uinfo and guid1 in uinfo[unm1]:
        msg_count = uinfo[unm1][guid1]["msg"]
        await event.reply(f"المستخدم [{uid1}](tg://user?id={unm1}) أرسل {msg_count} رسالة في هذه المجموعة.")
ABH.run_until_disconnected()
