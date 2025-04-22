import os
import requests
from telethon import TelegramClient, events, Button

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إعداد البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قائمة أسماء المستخدمين للقنوات
CHANNELS = ["x04ou", "EHIEX", "sszxl"]

# دالة check للتحقق من الاشتراك
def check(user_id, channel_username):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id=@{channel_username}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        if response.get("ok"):
            status = response["result"]["status"]
            print(f"User status in @{channel_username}: {status}")
            return status in ["member", "administrator", "creator"]
        else:
            print(f"Failed to check subscription for @{channel_username}: {response}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking subscription for @{channel_username}: {e}")
        return False

# التعامل مع الرسائل الخاصة
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id

    for channel_username in CHANNELS:
        if not check(user_id, channel_username):
            channel_link = f"https://t.me/{channel_username}"
            await event.respond(
                f"📌 للمتابعة، يرجى الاشتراك أولاً في القناة:\n{channel_link}",
                buttons=[Button.url("اضغط هنا للاشتراك", channel_link)]
            )
            return

    await event.respond("✅ مرحباً بك، أنت مشترك في جميع القنوات ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
