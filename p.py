import os
import requests
from telethon import TelegramClient, events, Button
from telethon.tl.functions.users import GetFullUser

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل (البوت)
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# قائمة القنوات بالترتيب
CHANNELS = ['@x04ou', '@EHIEX', '@sszxl']

# جلب user_id من username
async def get_user_id(username):
    try:
        user = await ABH(GetFullUser(username))
        return user.user.id
    except Exception as e:
        print(f"❌ خطأ في جلب ID للمستخدم @{username}: {e}")
        return None

# التحقق من الاشتراك في قناة واحدة
def is_user_subscribed_to_channel(user_id, channel):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        print(f"📡 التحقق من: {channel} | النتيجة: {response}")
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

    sender = await event.get_sender()
    username = sender.username

    if not username:
        await event.respond("⚠️ يجب أن يكون لديك اسم مستخدم @username للاستمرار.")
        return

    user_id = await get_user_id(username)
    if not user_id:
        await event.respond("❌ حدث خطأ أثناء التحقق من هويتك. حاول لاحقًا.")
        return

    # التحقق تدريجيًا من القنوات واحدة تلو الأخرى
    for channel in CHANNELS:
        if not is_user_subscribed_to_channel(user_id, channel):
            await event.respond(
                f"⚠️ للاستخدام الكامل، يجب عليك أولاً الاشتراك في القناة التالية:\n{channel}",
                buttons=[Button.url("📌 اضغط للاشتراك", f"https://t.me/{channel.strip('@')}")]
            )
            await event.delete()
            return

    # إذا كان مشتركًا في كل القنوات
    await event.respond("✅ مرحباً بك! أنت مشترك في جميع القنوات ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
