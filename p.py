import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# الحصول على المتغيرات من البيئة
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH'))
bot_token = os.getenv('BOT_TOKEN')

# إنشاء عميل Telethon
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# حقوق التقييد: إيقاف إرسال الرسائل بشكل دائم
restrict_rights = ChatBannedRights(
    until_date=None,  # لا يوجد تاريخ انتهاء
    send_messages=True,  # منع إرسال الرسائل
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True
)

# حقوق الرفع: السماح بإرسال الرسائل والوسائط
unrestrict_rights = ChatBannedRights(
    until_date=None,  # لا يوجد تاريخ انتهاء
    send_messages=False,  # السماح بإرسال الرسائل
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
    يراقب البوت أي عملية تقييد أو طرد تحدث في المجموعة، 
    إذا تم تقييد مستخدم، يعيد صلاحياته بعد 3 ثوان.
    """
    try:
        # التحقق من حالة "user_kicked" (طرد المستخدم)
        if event.user_kicked:
            user = await event.get_user()
            chat = await event.get_chat()

            # إيقاف إرسال الرسائل عند الطرد
            await client(EditBannedRequest(chat.id, user.id, unrestrict_rights))
            await event.reply(f"🚫 تم طرد {user.first_name} من المجموعة، ولا يمكنه إرسال الرسائل بعد الآن.")

        # التحقق من حالة "user_restricted" (تقييد المستخدم)
        if hasattr(event.original_update, 'banned_rights'):
            if event.original_update.banned_rights:
                user = await event.get_user()
                chat = await event.get_chat()

                # منع إرسال الرسائل
                await client(EditBannedRequest(chat.id, user.id, restrict_rights))
                await event.reply(f"🚫 تم تقييد {user.first_name} من إرسال الرسائل الآن.")

                # الانتظار 3 ثواني
                await asyncio.sleep(3)

                # إعادة حقوق المستخدم كما كانت
                try:
                    await client(EditBannedRequest(chat.id, user.id, unrestrict_rights))
                    await event.reply(f"✅ تم إعادة صلاحيات {user.first_name} لإرسال الرسائل.")
                except Exception as e:
                    print(f"خطأ أثناء إعادة الحقوق: {e}")

    except Exception as e:
        print(f"خطأ في معالجة الحدث: {e}")

client.start()
client.run_until_disconnected()
