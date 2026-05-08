import re, asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

def anymous_cmd(main_name, **kwargs):
    def decorator(f):
        # 1. جلب الاختصارات الخاصة بهذا الأمر فقط من Redis
        # نستخدم SMEMBERS لأنها الأسرع في جلب المجموعات الفريدة
        aliases = r.smembers(f"cmd:{main_name}") or []
        
        # 2. تحويل البيانات من bytes إلى string وتنظيفها
        patterns = [main_name]
        for a in aliases:
            patterns.append(a.decode('utf-8') if isinstance(a, bytes) else a)
        
        # 3. بناء Regex محصن ضد التداخل (Case-insensitive)
        # ^(?i) تجعل البوت يقرأ "تقييد" أو "تقييد" بنفس الكفاءة
        combined_pattern = f"^(?i)({'|'.join(patterns)})($|\s+)"
        
        @client.on(events.NewMessage(pattern=combined_pattern, **kwargs))
        async def wrapper(event):
            # معالجة متوازية لضمان عدم تأثر البوت بالرسائل الكثيرة
            asyncio.create_task(f(event))
        return f
    return decorator

# --- أوامر الإدارة المحدثة ---

@client.on(events.NewMessage(pattern=r'^ربط (\S+) (\S+)'))
async def add_alias(event):
    # استخدام: ربط تقييد تق
    try:
        orig, short = event.pattern_match.group(1), event.pattern_match.group(2)
        # تخزين الاختصار في مجموعة "الأمر الأصلي"
        r.sadd(f"cmd:{orig}", short)
        await event.reply(f"✅ تم إضافة `{short}` إلى مجموعة `{orig}`\nسوي ريستارت للتفعيل.")
    except: pass

@client.on(events.NewMessage(pattern=r'^حذف_ربط (\S+) (\S+)'))
async def remove_alias(event):
    # استخدام: حذف_ربط تقييد تق
    try:
        orig, short = event.pattern_match.group(1), event.pattern_match.group(2)
        r.srem(f"cmd:{orig}", short)
        await event.reply(f"🗑 تم حذف `{short}` من مجموعة `{orig}`")
    except: pass
@anymous_cmd('تقييد')
async def ban_handler(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"تم تقييد المستخدم {reply.sender_id}")
    else:
        await event.reply("رد على رسالة الشخص لتقييده")

@anymous_cmd('طرد')
async def kick_handler(event):
    await event.reply("تم الطرد")

# --- 3. أمر الربط (بدون رموز أيضاً) ---

