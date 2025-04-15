from telethon import TelegramClient, events
import os
import asyncio  # استخدم asyncio بدلاً من time

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage)
async def handler(event):
    channel = 'VIPABH'  # بدون @
    message_id = 1239

    try:
        msg = await ABH.get_messages(channel, ids=message_id)
        if msg and msg.media:
            msg = await event.respond("ها")
            await asyncio.sleep(3)  # استخدم asyncio.sleep
            await msg.edit(file=msg.media)
        else:
            await event.respond("تعذر العثور على الفيديو أو لا توجد وسائط في الرسالة.")
    except Exception as e:
        await event.respond(f"حدث خطأ: {str(e)}")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
