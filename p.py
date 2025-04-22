import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قراءة المتغيرات الحساسة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID', 'x04ou')  # افتراضي إذا لم يتم تعريفه

# التحقق من وجود المتغيرات الضرورية
if not all([api_id, api_hash, bot_token]):
    raise ValueError("❌ تأكد من تعيين المتغيرات: API_ID و API_HASH و BOT_TOKEN في ملف .env")

# تحويل API_ID إلى عدد صحيح
api_id = int(api_id)

# إنشاء جلسة البوت
bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# دالة التحقق من اشتراك المستخدم في القناة
def is_user_subscribed(user_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        response = requests.get(url, timeout=10).json()
        status = response["result"]["status"]
        return status in ["member", "administrator", "creator"]
    except (KeyError, requests.exceptions.RequestException):
        return False

# الاستجابة للرسائل الخاصة
@bot.on(events.NewMessage(incoming=True))
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
bot.run_until_disconnected()
