from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
from Resources import mention  # type: ignore
import os

# إعدادات الاتصال بالبوت
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

ABH = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# تعقب الأحداث الخاصة بالمجموعة (دخول، خروج، ترقية، حذف)
@ABH.on(events.ChatAction)
async def handler(event):
    try:
        if event.user_joined or event.user_added:
            user = await event.get_user()
            ment = await mention(event, user)
            await event.respond(f"👋 مرحباً {ment} في المجموعة!")
        elif event.user_left or event.user_kicked:
            user = await event.get_user()
            ment = await mention(event, user)
            await event.respond(f"👋 وداعاً {ment}، نتمنى لك التوفيق!")
        elif event.promoted:
            user = await event.get_user()
            ment = await mention(event, user)
            await event.respond(f"⭐ تم ترقية {ment} إلى مشرف.")
        elif event.demoted:
            user = await event.get_user()
            ment = await mention(event, user)
            await event.respond(f"⚠️ تم إزالة صلاحيات الإشراف من {ment}.")
    except Exception as e:
        print("حدث خطأ:", e)

# تشغيل البوت
ABH.run_until_disconnected()
