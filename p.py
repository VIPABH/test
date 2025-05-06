from telethon import TelegramClient, events, Button
import os

# إعدادات البوت من المتغيرات البيئية
api_id    = int(os.getenv('API_ID'))
api_hash  = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# إنشاء عميل التليجرام
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def promote(event):
    # نرسل رسالة نطلب فيها من المستخدم إرسال الصلاحيات،
    # مع إجبارهم على الرد عبر حقل "Force Reply"
    await event.reply(
        "ارسل الصلاحيات",
        buttons=Button.force_reply(selective=True)
    )

bot.run_until_disconnected()
