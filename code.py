from telethon import TelegramClient, events
import redis
from ABH import ABH as client
from Resources import * 

# 1. التأكد من وجود اتصال Redis (يستخدم المتغير r من ملف Resources)
# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# --- 2. السحر البرمجي (Monkey Patch) لـ Telethon ---
# حفظ الوظيفة الأصلية للمكتبة
original_message_init = events.NewMessage.Event.__init__

def patched_message_init(self, *args, **kwargs):
    """
    تعديل ذكي يقوم بفحص الرسالة وتغيير نصها إذا كانت اختصاراً
    قبل أن تصل إلى أي Handler في الـ 140 أمر.
    """
    # في أغلب إصدارات Telethon، الرسالة تكون أول وسيط في args
    if args:
        message = args[0]
        # التأكد أن الكائن هو رسالة نصية وليس حدثاً فارغاً
        if hasattr(message, 'message') and message.message:
            text = message.message
            
            # فحص إذا كانت الرسالة تبدأ برموز الأوامر (/ . !)
            if text.startswith(('/', '.', '!')):
                prefix = text[0]
                parts = text.split(maxsplit=1)
                trigger = parts[0][1:] # الكلمة بدون الرمز
                rest = parts[1] if len(parts) > 1 else ""

                # جلب الأصل من Redis (مثلاً: ها -> تقييد)
                real_cmd = r.hget("bot_aliases", trigger)
                if real_cmd:
                    # تنظيف الكلمة وبناء النص الجديد
                    clean_cmd = real_cmd.lstrip('/.! ')
                    new_text = f"{prefix}{clean_cmd} {rest}".strip()
                    
                    # تعديل النص داخل كائن الرسالة الأصلي
                    message.message = new_text
                    if hasattr(message, 'text'):
                        message.text = new_text
                    
                    # طباعة للتأكد في السكرين
                    print(f"🛠 [Alias Patch] تم تحويل: {trigger} -> {clean_cmd}")

    # استدعاء وظيفة المكتبة الأصلية مع تمرير كل الوسائط كما هي
    # هذا السطر يحل مشكلة الـ TypeError نهائياً
    original_message_init(self, *args, **kwargs)

# تطبيق التعديل على المكتبة
events.NewMessage.Event.__init__ = patched_message_init

# --- 3. أوامر إدارة الاختصارات (للمطور فقط) ---
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
        await event.reply(f"✅ **تم الربط بنجاح**\n\nالأصل: `{original}`\nالاختصار: `{short}`")
    except:
        await event.reply("⚠️ الاستخدام: `/ربط الأمر_الأصلي الاختصار`")

@client.on(events.NewMessage(pattern=r'^/حذف_ربط (.*)'))
async def del_alias_cmd(event):
    if event.sender_id != OWNER_ID:
        return
    short = event.pattern_match.group(1).replace('/', '').strip()
    if r.hdel("bot_aliases", short):
        await event.reply(f"🗑 تم حذف الاختصار `{short}`")
    else:
        await event.reply("❌ الاختصار غير موجود.")

# --- 4. الـ 140 أمر لديك سيعملون تلقائياً هنا ---
# مثال:
# @client.on(events.NewMessage(pattern='/تقييد'))
# async def ban(event): ...

print("🚀 Anymous Bot is patched and running successfully!")
