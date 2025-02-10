import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# الحصول على المتغيرات من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء عميل Telethon
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# الحقوق عند التقييد (منع الإرسال والكتابة لمدة 30 دقيقة)
restrict_rights = ChatBannedRights(
    until_date=None,  # التقييد يدويًا (سيتم إزالته بعد 30 دقيقة من خلال الكود)
    send_messages=True,  
    send_media=True,  
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

# الحقوق عند رفع التقييد (إعادة الصلاحيات)
unrestrict_rights = ChatBannedRights(
    until_date=None,  
    send_messages=False,  
    send_media=False,  
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False
)

@client.on(events.ChatAction)
async def auto_unrestrict(event):
    """
    يراقب البوت أي عملية تقييد تحدث في المجموعة، 
    إذا تم تقييد مستخدم، يعيد صلاحياته بعد 30 دقيقة.
    """
    if event.restricted:
        user = await event.get_user()
        chat = await event.get_chat()

        # التأكد من أن المستخدم تم منعه من إرسال الرسائل
        if event.restricted.default_banned_rights.send_messages:
            await event.reply(f"🚫 تم تقييد {user.first_name} لمدة 30 دقيقة.")

            # انتظار 30 دقيقة (1800 ثانية)
            await asyncio.sleep(1)

            # رفع التقييد تلقائيًا
            await client(EditBannedRequest(chat.id, user.id, unrestrict_rights))
            await event.reply(f"✅ تم رفع التقييد عن {user.first_name} بعد 30 دقيقة.")

client.start()
client.run_until_disconnected()
