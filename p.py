import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
CHANNEL_ID = 'x04ou'

# دالة التحقق من الاشتراك
def is_user_subscribed(user_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    response = requests.get(url).json()
    try:
        status = response["result"]["status"]
        return status in ["member", "administrator", "creator"]
    except KeyError:
        return False

# مراقبة الرسائل الخاصة فقط
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id
    if not is_user_subscribed(user_id):
        channel_link = f"https://t.me/{CHANNEL_ID.strip('@')}"
        await event.respond(
            f"📌 للمتابعة، يرجى الاشتراك أولاً في القناة:\n{CHANNEL_ID}",
            buttons=[Button.url("اضغط هنا للاشتراك", channel_link)]
        )
        await event.delete()
        return

    await event.respond("✅ مرحباً بك، أنت مشترك ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.start()
ABH.run_until_disconnected()
