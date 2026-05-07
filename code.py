from telethon import TelegramClient, events
import redis
from ABH import ABH
from Resources import * as client
# معرف المطور (أنت) للتحكم بالاختصارات
OWNER_ID = wfffp  # ضع أيديك هنا

# --- 1. الموزع الذكي (الميدل وير) ---
# هذا الجزء هو المسؤول عن تحويل "تق" إلى "تقييد" تلقائياً قبل وصولها للأوامر
@client.on(events.NewMessage(incoming=True))
async def alias_resolver(event):
    if not event.text or not event.text.startswith(('/', '.')):
        return

    # تفكيك النص: /تق المستخدم -> الكلمة هي "تق"
    parts = event.text.split(maxsplit=1)
    prefix = parts[0][0]  # يجلب الرمز / أو .
    trigger = parts[0][1:] # يجلب اسم الأمر بدون الرمز
    args = parts[1] if len(parts) > 1 else ""

    # البحث في Redis عن الأمر الأصلي المرتبط بهذا الاختصار
    real_command_name = r.hget("bot_aliases", trigger)

    if real_command_name:
        # إعادة بناء نص الرسالة بالأمر الأصلي
        new_text = f"{prefix}{real_command_name} {args}".strip()
        
        # تعديل الحدث داخلياً (الـ 140 أمر سيقرأون النص الجديد)
        event.message.message = new_text
        event.message.text = new_text
        
        # إعادة توجيه الحدث المعدل للمشروع
        await client._dispatch_event(event)
        
        # إيقاف معالجة النص القديم (الاختصار) لمنع التكرار
        raise events.StopPropagation

# --- 2. أمر التحكم بالاختصارات (للمطور فقط) ---
@client.on(events.NewMessage(pattern=r'/(ربط|unalias) (.*)'))
async def manage_aliases(event):
    if event.sender_id != OWNER_ID:
        return

    cmd_type = event.pattern_match.group(1)
    data = event.pattern_match.group(2).split()

    if cmd_type == "ربط":
        if len(data) < 2:
            return await event.reply("❌ الاستخدام: `/ربط تقييد تق`")
        
        original, short = data[0], data[1]
        r.hset("bot_aliases", short, original)
        await event.reply(f"✅ تم! الآن `{short}` سيقوم بتنفيذ `{original}`")

    elif cmd_type == "unalias":
        short = data[0]
        if r.hdel("bot_aliases", short):
            await event.reply(f"🗑 تم حذف الاختصار `{short}`")

# --- مثال لواحد من الـ 140 أمر لديك (لا يحتاج تعديل) ---
@client.on(events.NewMessage(pattern='/تقييد'))
async def ban_handler(event):
    # هذا الأمر سيعمل سواء كتب المستخدم /تقييد أو كتب الاختصار الذي ربطته
    await event.reply("بشري، تم تنفيذ أمر التقييد بنجاح! 🔥")

# تشغيل البوت
print("Anymous Bot is running...")
