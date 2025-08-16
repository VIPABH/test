import os
from telethon import TelegramClient, events
from tinydb import TinyDB, Query

# قراءة المتغيرات البيئية
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إنشاء عميل Telethon
client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

target_file_id = None  # نخزن هنا الـ file_id للمتحرك

# أمر لتعيين الـ file_id عبر الرد
@client.on(events.NewMessage(pattern=r"^/ضعمتحرك$"))
async def set_file_id(event):
    global target_file_id
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.document:
            target_file_id = reply_msg.file.id
            await event.reply("✅ تم حفظ المتحرك.")
        else:
            await event.reply("❌ الرد يجب أن يكون على متحرك.")
    else:
        await event.reply("❌ يجب الرد على المتحرك.")

# مراقبة الرسائل وحذف أي رسالة بنفس الـ file_id
@client.on(events.NewMessage)
async def delete_matching(event):
    global target_file_id
    reply_msg = await event.get_reply_message()
    if target_file_id and event.document:
        if event.file.id == target_file_id:
            await reply_msg.delete()

client.run_until_disconnected()
