import redis
from ABH import *
from telethon import TelegramClient, events

# --- نظام معالجة الاختصارات (The Core) ---

@ABH.on(events.NewMessage(incoming=True))
async def alias_resolver(event):
    # نحدد الرموز التي يبدأ بها الأمر
    prefixes = ('.', '/', '!')
    if not event.raw_text.startswith(prefixes):
        return

    chat_id = event.chat_id
    text_parts = event.raw_text.split()
    
    # فصل الرمز عن الكلمة (مثلاً .تق -> الرمز . والكلمة تق)
    prefix = text_parts[0][0]
    cmd_name = text_parts[0][1:]

    # البحث في Redis عن اختصار مخصص لهذه المجموعة
    # الـ Key يكون مثلاً: aliases:-100123456789
    real_command = r.hget(f"aliases:{chat_id}", cmd_name)

    if real_command:
        # إذا وجدنا اختصار، نقوم باستبداله في النص الأصلي للـ event
        # هذا التغيير سيؤثر على كل الـ handlers القادمة
        args = " ".join(text_parts[1:])
        event.raw_text = f"{prefix}{real_command} {args}".strip()
        print(f"🔄 Alias Triggered: {cmd_name} -> {real_command}")

# --- أوامر التحكم بالاختصارات ---

@ABH.on(events.NewMessage(pattern=r'^[\.\/]اختصار (\S+) (\S+)'))
async def set_alias(event):
    # الاستخدام: .اختصار تق تقييد
    # يجب إضافة فحص هنا للتأكد أن المرسل أدمن أو المطور (علي هاشم)
    
    alias_name = event.pattern_match.group(1)
    original_cmd = event.pattern_match.group(2)
    chat_id = event.chat_id

    try:
        r.hset(f"aliases:{chat_id}", alias_name, original_cmd)
        await event.reply(f"✅ تم حفظ الاختصار:\n**{alias_name}** ← **{original_cmd}**")
    except Exception as e:
        await event.reply(f"❌ خطأ في Redis: {e}")

@ABH.on(events.NewMessage(pattern=r'^[\.\/]حذف_اختصار (\S+)'))
async def del_alias(event):
    alias_name = event.pattern_match.group(1)
    chat_id = event.chat_id
    
    if r.hdel(f"aliases:{chat_id}", alias_name):
        await event.reply(f"🗑 تم حذف الاختصار `{alias_name}`")
    else:
        await event.reply("⚠️ هذا الاختصار غير موجود أصلاً.")

# --- أمثلة على أوامر البوت (التي سيتم استدعاؤها بالاختصار) ---

@ABH.on(events.NewMessage(pattern=r'^[\.\/]تقييد'))
async def ban_user(event):
    await event.reply("🚫 جاري تنفيذ أمر التقييد العام...")

@ABH.on(events.NewMessage(pattern=r'^[\.\/]كشف'))
async def check_user(event):
    await event.reply("🔍 جاري فحص سجل المستخدم...")

print("✅ Bot is running...")
