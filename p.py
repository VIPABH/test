import os
import requests
from telethon import TelegramClient, events, Button

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إعداد البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# إعداد القناة
CHANNEL_ID = -1002116581783
CHANNEL_USERNAME = "x04ou"

# دالة check للتحقق من الاشتراك
def check(user_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        if response.get("ok"):
            status = response["result"]["status"]
            print(f"User status: {status}")
            return status in ["member", "administrator", "creator"]
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False

# التعامل مع الرسائل الجديدة
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id

    # التحقق من الاشتراك في القناة
    if not check(user_id):
        channel_link = f"https://t.me/{CHANNEL_USERNAME}"
        await event.respond(
            f"📌 للمتابعة، يرجى الاشتراك أولاً في القناة:\n{channel_link}",
            buttons=[Button.url("اضغط هنا للاشتراك", channel_link)]
        )
        return

    # الرد على المستخدم إذا كان مشتركًا في القناة
    await event.respond("✅ مرحباً بك، أنت مشترك في القناة ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
