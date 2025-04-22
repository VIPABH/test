import os
from telethon import TelegramClient, events
from telethon.tl.functions.channels import ToggleReactionsRequest
from telethon.tl.types import ChatReactionsNone, ChatReactionsAll

# إعدادات الاتصال
api_id = int(os.getenv("API_ID", "123456"))  # ضع api_id أو خزنه كمتغير بيئة
api_hash = os.getenv("API_HASH", "your_api_hash")
session_name = "session"

# اسم المستخدم أو آيدي المجموعة
group_username = os.getenv("GROUP_USERNAME", "your_group_username")

# بدء الجلسة
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(pattern=r'^/reactions (on|off)$'))
async def toggle_reactions(event):
    if not event.is_group:
        await event.reply("هذا الأمر متاح فقط في المجموعات.")
        return

    command = event.pattern_match.group(1)
    group = await client.get_entity(group_username)

    if command == "off":
        await client(ToggleReactionsRequest(
            channel=group,
            reactions=ChatReactionsNone()
        ))
        os.environ["REACTIONS_STATE"] = "off"
        await event.reply("تم تعطيل التفاعلات.")
    else:
        await client(ToggleReactionsRequest(
            channel=group,
            reactions=ChatReactionsAll()
        ))
        os.environ["REACTIONS_STATE"] = "on"
        await event.reply("تم تفعيل التفاعلات.")

# تشغيل الكلاينت
client.start()
print("Bot is running...")
client.run_until_disconnected()
