import os
import requests
from telethon import TelegramClient, events, Button

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل (البوت)
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
CHANNEL_ID = -1002116581783  # تأكد من أن هذا هو ID القناة أو اسمها الصحيح (مثلاً '@channel_username')

# دالة التحقق من الاشتراك في القناة باستخدام API الخاص بالبوت
def is_user_subscribed(user_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        print("Response:", response)  # طباعة الرد الكامل للتفاصيل
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

# مراقبة الرسائل الخاصة فقط
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    user_id = event.sender_id
    if not is_user_subscribed(user_id):
        # إذا لم يكن مشتركًا في القناة، أرسل رسالة اشتراك
        channel_link = f"https://t.me/{CHANNEL_ID}"
        await event.respond(
            f"📌 للمتابعة، يرجى الاشتراك أولاً في القناة:\n{channel_link}",
            buttons=[Button.url("اضغط هنا للاشتراك", channel_link)]
        )
        await event.delete()
        return

    # إذا كان مشتركًا بالفعل، يمكنه استخدام البوت
    await event.respond("✅ مرحباً بك، أنت مشترك ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
