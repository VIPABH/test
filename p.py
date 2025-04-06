import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityUrl

# إعدادات البوت
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.MessageEdited)
async def test(event):
    msg = event.message

    # تحقق إذا كانت الرسالة تحتوي على وسائط أو ملف أو رابط
    has_media = bool(msg.media)
    has_document = bool(msg.document)
    has_url = any(isinstance(entity, MessageEntityUrl) for entity in (msg.entities or []))

    if has_media or has_document or has_url:
        await event.reply('ها شعدلت ولك! الرابط أو الملف أو الوسائط تم تعديلها.')
    else:
        return  # لا ترسل شيء إذا ما كانت تحتوي على أحد هذه الأنواع

# بدء البوت
ABH.run_until_disconnected()
