from telethon import TelegramClient, events
from datetime import datetime
import os, asyncio

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

ABH = TelegramClient("code", api_id, api_hash).start(bot_token=bot_token)
uinfo = {}

@ABH.on(events.NewMessage)
async def msgs(event):
    if event.is_group:
        uid = event.sender.first_name
        unm = event.sender_id
        guid = event.chat_id

        uinfo.setdefault(unm, {}).setdefault(guid, {"guid": guid, "unm": unm, "fname": uid, "msg": 0})["msg"] += 1


        now = datetime.now().strftime("%I:%M %p")
        target_time = "02:28 PM"

        if now == target_time:
            print(f"{now} - is it")
        else:
            print(f"is not {now}")
@ABH.on(events.NewMessage(pattern='توب'))
async def show_top(event):
    await asyncio.sleep(2)
    guid = event.chat_id
    top_users = []

    # تصفية وفرز المستخدمين حسب عدد الرسائل
    sorted_users = sorted(
        ((user, data[guid]) for user, data in uinfo.items() if guid in data),
        key=lambda x: x[1]['msg'],
        reverse=True
    )[:15]

    for user_id, data in sorted_users:
        top_users.append(f"المستخدم [{data['fname']}](tg://user?id={user_id}) رسائله -> {data['msg']}")

    await event.reply("\n".join(top_users) if top_users else "لا توجد بيانات لعرضها.")

ABH.run_until_disconnected()
