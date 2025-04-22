import os
import requests
from telethon import TelegramClient, events, Button

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إعداد البوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قائمة القنوات التي سيتم التحقق من الاشتراك فيها
CHANNELS = [
    {'channel_id': -1002116581783, 'channel_username': 'x04ou'},
    {'channel_id': -1001897025581, 'channel_username': 'EHIEX'},
    {'channel_id': -1002055758177, 'channel_username': 'sszxl'}
]

# التحقق من الاشتراك في القناة
def is_user_subscribed(user_id, channel_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel_id}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        print("Response:", response)

        if response.get("ok"):
            status = response["result"]["status"]
            print(f"User status: {status}")
            return status in ["member", "administrator", "creator"]
        else:
            print(f"Failed to get user status. Response: {response}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False

@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id
    not_subscribed_channels = []

    # التحقق من الاشتراك في كل قناة
    for channel in CHANNELS:
        if not is_user_subscribed(user_id, channel['channel_id']):
            not_subscribed_channels.append(channel)

    if not_subscribed_channels:
        # إرسال زر لكل قناة لم يتم الاشتراك فيها
        buttons = []
        for channel in not_subscribed_channels:
            channel_link = f"https://t.me/{channel['channel_username']}"
            buttons.append(Button.url(f"📌 اضغط للاشتراك في {channel['channel_username']}", channel_link))

        await event.respond(
            f"⚠️ للاستخدام الكامل، يرجى الاشتراك في القنوات التالية:",
            buttons=buttons
        )
        await event.delete()
        return

    await event.respond("✅ مرحباً بك، أنت مشترك في جميع القنوات ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
