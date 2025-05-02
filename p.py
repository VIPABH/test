from telethon import TelegramClient, events
import re
import asyncio
import os

# إعدادات API
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')

ABH = TelegramClient('s', api_id, api_hash)

# الديكوريتور المعدل
def reply_or_mention_or_id_only(func):
    async def wrapper(event):
        message = event.message
        client = event.client  # هذا هو ABH

        me = await client.get_me()
        my_id = me.id
        my_username = me.username

        # شرط 1: الرد على رسالة أرسلتها أنت
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id == my_id:
                return await func(event)

        # شرط 2: منشن لليوزر الخاص بك
        if my_username and f"@{my_username.lower()}" in message.raw_text.lower():
            return await func(event)

        # شرط 3: تحتوي على الآيدي الخاص بك كرقم
        if re.search(rf'\b{my_id}\b', message.raw_text):
            return await func(event)

        # إذا لم تتحقق الشروط، لا يتم تنفيذ الدالة
        return
    return wrapper

# ربط الحدث بالديكوريتور
@ABH.on(events.NewMessage)
@reply_or_mention_or_id_only
async def handle_targeted_messages(event):
    await event.reply("تم التعرف على الرسالة كـ رد، منشن، أو تحتوي على آيدي.")

# تشغيل الكلاينت
async def main():
    await ABH.start()
    await ABH.run_until_disconnected()

asyncio.run(main())
