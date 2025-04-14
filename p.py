from telethon import TelegramClient, events
import logging, os

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
# إعداد العميل للبوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# إعدادات تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# الدالة التي تعرض لقب المشرف الخاص بك
@ABH.on(events.NewMessage(pattern='لقبي'))
async def nickname(event):
    chat = await event.get_chat()  # الحصول على الدردشة
    sender_id = event.sender_id  # الحصول على ID المستخدم الذي أرسل الرسالة
    try:
        # الحصول على معلومات المشرف من الدردشة
        participant = await ABH.get_participant(chat, sender_id)
        nickname = participant.custom_title or "لا يوجد لقب"
        await event.reply(f"لقبك ↞ {nickname}")
    except Exception as e:
        await event.reply("لم يتم العثور على المشرف.")
        logging.error(f"Error: {str(e)}")

# دالة لعرض لقب الشخص الذي تم الرد عليه
@ABH.on(events.NewMessage(pattern='لقبه'))
async def nickname_r(event):
    chat = await event.get_chat()  # الحصول على الدردشة
    msg = await event.get_reply_message()  # الحصول على الرسالة التي تم الرد عليها
    sender_id = msg.sender_id  # الحصول على ID الشخص الذي تم الرد عليه
    try:
        # الحصول على معلومات المشرف من الدردشة
        participant = await ABH.get_participant(chat, sender_id)
        nickname = participant.custom_title or "لا يوجد لقب"
        await event.reply(f"لقبه ↞ {nickname}")
    except Exception as e:
        await event.reply("لم يتم العثور على المشرف.")
        logging.error(f"Error: {str(e)}")

# بدء البوت
ABH.start()

# تشغيل البوت بشكل مستمر
ABH.run_until_disconnected()
