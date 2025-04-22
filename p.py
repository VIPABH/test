import os
import requests
from telethon import TelegramClient, events, Button
from telethon.tl.functions.users import GetFullUserRequest

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل (البوت)
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قائمة أسماء القنوات أو المجموعات (usernames)
CHANNELS = ['@x04ou', '@EHIEX', '@sszxl']

# جلب user_id من username
async def get_user_id(username):
    try:
        user_full = await ABH(GetFullUserRequest(username))  # الحصول على التفاصيل الكاملة
        return user_full.user.id  # الوصول إلى الـ user من الكائن المسترجع
    except Exception as e:
        print(f"❌ خطأ في جلب ID للمستخدم @{username}: {e}")
        return None

# التحقق من الاشتراك في القنوات واحدة تلو الأخرى
def check_subscription(user_id):
    for channel in CHANNELS:
        url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel}&user_id={user_id}"
        try:
            response = requests.get(url).json()
            if not response.get("ok") or response["result"]["status"] not in ["member", "administrator", "creator"]:
                return channel  # يرجع القناة التي لم يشترك فيها
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال بـ Telegram API: {e}")
            return channel
    return None  # مشترك في الكل

# معالج الرسائل الخاصة
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    username = sender.username

    if not username:
        await event.respond("⚠️ يجب أن يكون لديك اسم مستخدم @username للاستمرار.")
        return

    user_id = await get_user_id(username)
    if not user_id:
        await event.respond("❌ حدث خطأ أثناء التحقق من هويتك. حاول لاحقًا.")
        return

    not_subscribed_channel = check_subscription(user_id)
    if not_subscribed_channel:
        channel_link = f"https://t.me/{not_subscribed_channel.strip('@')}"
        await event.respond(
            f"⚠️ للاستخدام الكامل، يرجى الاشتراك أولاً في القناة التالية:\n{not_subscribed_channel}",
            buttons=[Button.url("📌 اضغط للاشتراك", channel_link)]
        )
        await event.delete()
        return

    await event.respond("✅ مرحباً بك! أنت مشترك في جميع القنوات ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
