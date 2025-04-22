import os
import requests
from telethon import TelegramClient, events, Button

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل (البوت)
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قائمة القنوات بالترتيب
CHANNELS = ['@x04ou', '@EHIEX', '@sszxl']

# التحقق من اشتراك المستخدم في قناة معينة
def check_subscription(user_id, channel_username):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel_username}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        print(f"📡 التحقق من: {channel_username} | النتيجة: {response}")
        if response.get("ok") and response["result"]["status"] in ["member", "administrator", "creator"]:
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال بـ Telegram API: {e}")
        return False

# معالج الرسائل الخاصة
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id

    # التحقق من كل قناة بالتسلسل
    for channel in CHANNELS:
        if not check_subscription(user_id, channel):
            await event.respond(
                f"📌 للاستخدام الكامل، يرجى أولاً الاشتراك في القناة التالية:\n{channel}",
                buttons=[Button.url("اضغط للاشتراك", f"https://t.me/{channel.strip('@')}")]
            )
            await event.delete()
            return

    # إذا كان مشتركًا في جميع القنوات
    await event.respond("✅ مرحباً بك! أنت مشترك في جميع القنوات ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
