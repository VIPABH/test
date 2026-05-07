from telethon import TelegramClient, events
import redis
import re
from ABH import ABH as client
from Resources import * 

# 1. إعداد الاتصال بـ Redis (تأكد من استخدام المتغير 'r' الموجود في Resources)
# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# --- 2. السحر البرمجي: تعديل كلاس المكتبة داخلياً ---
# نقوم بحفظ الوظيفة الأصلية للمكتبة قبل تعديلها
original_message_init = events.NewMessage.Event.__init__

def patched_message_init(self, chat, message, getattr_utils):
    if message and message.message:
        text = message.message
        # التحقق إذا كانت الرسالة تبدأ بالرموز المستخدمة في سورس Anymous
        if text.startswith(('/', '.', '!')):
            prefix = text[0]
            parts = text.split(maxsplit=1)
            trigger = parts[0][1:]  # استخراج الكلمة (مثلاً: ها)
            args = parts[1] if len(parts) > 1 else ""

            # جلب الأمر الأصلي من Redis (مثلاً: تقييد)
            # البحث يتم بشكل لحظي؛ أي ربط جديد سيعمل فوراً بدون ريستارت
            real_cmd = r.hget("bot_aliases", trigger)
            
            if real_cmd:
                # تنظيف الكلمة المسترجعة وبناء النص الجديد
                clean_real_cmd = real_cmd.lstrip('/.! ')
                new_text = f"{prefix}{clean_real_cmd} {args}".strip()
                
                # تغيير محتوى الرسالة في قلب النظام
                message.message = new_text
                if hasattr(message, 'text'):
                    message.text = new_text
                
                # طباعة في الـ screen للتأكد من نجاح العملية
                print(f"🛠 [Alias System] تم تحويل ({trigger}) إلى ({clean_real_cmd})")

    # تشغيل وظيفة المكتبة الأصلية مع النص الجديد
    original_message_init(self, chat, message, getattr_utils)

# تطبيق التعديل "الجيني" على Telethon
events.NewMessage.Event.__init__ = patched_message_init

# --- 3. أوامر التحكم (للمطور فقط) ---
@client.on(events.NewMessage(pattern=r'^/ربط (.*)'))
async def add_alias_cmd(event):
    if event.sender_id != OWNER_ID:
        return
    try:
        # الاستخدام: /ربط تقييد ها
        data = event.pattern_match.group(1).split()
        original = data[0].replace('/', '').strip()
        short = data[1].replace('/', '').strip()
        
        r.hset("bot_aliases", short, original)
        await event.reply(f"✅ **تم الربط بنجاح**\n\nالأصل: `{original}`\nالاختصار: `{short}`\n\n*الآن جرب إرسال `{short}` وسيعمل كأنه `{original}` تماماً.*")
    except Exception as e:
        await event.reply("⚠️ خطأ! الاستخدام الصحيح: `/ربط الأمر_الأصلي الاختصار`")

@client.on(events.NewMessage(pattern=r'^/حذف_ربط (.*)'))
async def del_alias_cmd(event):
    if event.sender_id != OWNER_ID:
        return
    short = event.pattern_match.group(1).replace('/', '').strip()
    if r.hdel("bot_aliases", short):
        await event.reply(f"🗑 تم حذف الاختصار `{short}`")
    else:
        await event.reply("❌ الاختصار غير موجود.")

# --- 4. مثال للـ 140 أمر (لا تلمس كودها، ستبقى كما هي) ---
@client.on(events.NewMessage(pattern='/تقييد'))
async def ban_handler(event):
    # سيعمل هذا الأمر تلقائياً عند كتابة /تقييد أو الاختصار المربوط به
    if event.is_reply:
        await event.reply("تم تنفيذ أمر التقييد بنجاح! 🔥")

# تشغيل البوت
print("🚀 Anymous Bot is running with Advanced Patching System...")
