from telethon import TelegramClient, events
from telethon.tl.types import ReplyMarkup, ForceReply  # استيراد ForceReply وReplyMarkup
import os

# إعدادات البوت
api_id = os.getenv('API_ID')  # استخدم البيئة لتخزين API_ID
api_hash = os.getenv('API_HASH')  # استخدم البيئة لتخزين API_HASH
bot_token = os.getenv('BOT_TOKEN')  # استخدم البيئة لتخزين BOT_TOKEN

# إنشاء العميل للبوت
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# التعامل مع الحدث عندما يتم إرسال رسالة بالصيغة "رفع مشرف"
@ABH.on(events.NewMessage(pattern="^رفع مشرف.$"))
async def promote(event):
    # إرسال رسالة للمستخدم تطلب منه إرسال الصلاحيات
    await event.reply(
        "ارسل الصلاحيات",
        reply_markup=ForceReply(selective=True)  # استخدام ForceReply هنا
    )

# تشغيل العميل
ABH.run_until_disconnected()
