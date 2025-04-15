from telethon import TelegramClient, events
import os
import asyncio

# تحميل متغيرات البيئة
api_id = int(os.getenv('API_ID', '123456'))
api_hash = os.getenv('API_HASH', 'your_api_hash')
bot_token = os.getenv('BOT_TOKEN', 'your_bot_token')

# إنشاء جلسة البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage)
async def handler(event):
    channel = 'VIPABH'
    message_id = 1239

    try:
        msg_from_channel = await ABH.get_messages(channel, ids=message_id)
        if msg_from_channel and msg_from_channel.media:
            # إرسال رسالة أولية
            msg = await event.respond("ها")

            # انتظار 3 ثواني
            await asyncio.sleep(3)

            # تعديل الرسالة النصية
            await msg.edit("تم التحديث بعد 3 ثوانٍ.")

            # إرسال الفيديو في رسالة جديدة (لا يمكن دمجه مع التعديل)
            #await event.respond(file=msg_from_channel.media)
        else:
            await event.respond("تعذر العثور على الفيديو أو لا توجد وسائط في الرسالة.")
    except Exception as e:
        await event.respond(f"حدث خطأ: {str(e)}")

print("🤖 البوت يعمل الآن...")
ABH.run_until_disconnected()
