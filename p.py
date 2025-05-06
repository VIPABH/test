from telethon import TelegramClient, events
from telethon.tl.types import ReplyKeyboardForceReply
import os

# إعدادات البوت
api_id    = os.getenv('API_ID')
api_hash  = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء عميل التليجرام
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern="^رفع مشرف$"))
async def promote(event):
    # يرسل رسالة ويجبر المستخدم على الرد عليها
    await event.reply(
        "ارسل الصلاحيات",
        reply_markup=ReplyKeyboardForceReply(
            selective=True,    # يظهر فقط للمرسل لا للجميع :contentReference[oaicite:0]{index=0}
            single_use=True    # يُخفي الرباي كيبورد بعد الرد مرة واحدة :contentReference[oaicite:1]{index=1}
        )
    )

client.run_until_disconnected()
