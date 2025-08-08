import os
from telethon import TelegramClient, events
from tinydb import TinyDB, Query

# قراءة المتغيرات البيئية
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء عميل Telethon
client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

# إنشاء قاعدة بيانات TinyDB
db = TinyDB("data.json")
users_table = db.table("users")
User = Query()

# حدث استقبال رسالة
@client.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    username = sender.username if sender.username else "بدون اسم"

    if not users_table.contains(User.id == user_id):
        users_table.insert({"id": user_id, "username": username, "messages": 1})
        await event.reply("👋 أهلاً بك! تم تسجيلك في قاعدة البيانات.")
    else:
        users_table.update_increment("messages", User.id == user_id)
        user_data = users_table.get(User.id == user_id)
        await event.reply(f"📊 عدد رسائلك المسجلة: {user_data['messages']}")

print("✅ البوت يعمل الآن...")
client.run_until_disconnected()
