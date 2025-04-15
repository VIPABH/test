from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import os

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'id'))
async def handler(event):
    sender_id = event.sender_id
    user = await ABH.get_entity(sender_id)    
    await event.reply(f"⚠️ حدث خطأ:\n`{str(e)}`")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
