import os
from telethon import TelegramClient, events, Button
from telethon.errors import UserAlreadyParticipantError

# تحميل المتغيرات من البيئة
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إنشاء العميل (البوت)
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
CHANNEL_ID = 'x04ou'  # يمكن أن يكون اسم القناة أو الـ chat_id (احرص على أنه صحيح)

# دالة التحقق من الاشتراك في القناة باستخدام Telethon
async def is_user_subscribed(user_id):
    try:
        # نحاول الحصول على حالة العضوية للمستخدم في القناة
        member = await ABH.get_participant(CHANNEL_ID, user_id)
        return True  # إذا تم العثور على المستخدم كعضو، فإن المستخدم مشترك
    except ValueError:
        # إذا لم يتم العثور على المستخدم في القناة، يعاد False
        return False

# مراقبة الرسائل الخاصة فقط
@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private:
        return

    user_id = event.sender_id
    if not await is_user_subscribed(user_id):
        # إذا لم يكن مشتركًا في القناة، أرسل رسالة اشتراك
        channel_link = f"https://t.me/{CHANNEL_ID.strip('@')}"
        await event.respond(
            f"📌 للمتابعة، يرجى الاشتراك أولاً في القناة:\n{CHANNEL_ID}",
            buttons=[Button.url("اضغط هنا للاشتراك", channel_link)]
        )
        await event.delete()
        return

    # إذا كان مشتركًا بالفعل، يمكنه استخدام البوت
    await event.respond("✅ مرحباً بك، أنت مشترك ويمكنك استخدام البوت.")

# تشغيل البوت
ABH.run_until_disconnected()
