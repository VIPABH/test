import re
import asyncio
from telethon import events
from ABH import ABH as client
from Resources import * # =====================================================================
# 1. الديكوريتور الذكي (نظام المجموعات المنفصلة في Redis لأعلى أداء)
# =====================================================================
def anymous_cmd(main_name, **kwargs):
    def decorator(f):
        # جلب الاختصارات الخاصة بهذا الأمر فقط من Redis باستخدام الـ Sets (الأسرع على الإطلاق)
        aliases = r.smembers(f"cmd:{main_name}") or []
        
        # تحويل الاختصارات من bytes إلى نصوص عادية وتنظيفها
        patterns = [main_name]
        for a in aliases:
            patterns.append(a.decode('utf-8') if isinstance(a, bytes) else a)
        
        # بناء نمط Regex محصن ضد تداخل الكلمات ومستقر تحت ضغط الرسائل الهائل
        combined_pattern = f"^(?i)({'|'.join(patterns)})($|\s+)"
        
        @client.on(events.NewMessage(pattern=combined_pattern, **kwargs))
        async def wrapper(event):
            # معالجة متوازية لضمان عدم تأثر البوت نهائياً بضغط الرسائل وتفادي التجميد
            asyncio.create_task(f(event))
        return f
    return decorator

# =====================================================================
# 2. أوامر الإدارة (الربط والحذف)
# =====================================================================

@client.on(events.NewMessage(pattern=r'^ربط (\S+) (\S+)'))
async def add_alias(event):
    # الاستخدام: ربط تقييد تق
    try:
        orig = event.pattern_match.group(1).replace('/', '').strip()
        short = event.pattern_match.group(2).replace('/', '').strip()
        
        # إضافة الاختصار للمجموعة الخاصة بالأمر الأصلي داخل Redis
        r.sadd(f"cmd:{orig}", short)
        await event.reply(f"✅ تم إضافة الاختصار `{short}` إلى مجموعة `{orig}`\n🔄 يرجى إعادة تشغيل السورس للتفعيل.")
    except Exception:
        await event.reply("⚠️ الاستخدام: `ربط تقييد تق`")

@client.on(events.NewMessage(pattern=r'^حذف_ربط (\S+) (\S+)'))
async def remove_alias(event):
    # الاستخدام: حذف_ربط تقييد تق
    try:
        orig = event.pattern_match.group(1).replace('/', '').strip()
        short = event.pattern_match.group(2).replace('/', '').strip()
        
        # حذف الاختصار من مجموعة Redis
        r.srem(f"cmd:{orig}", short)
        await event.reply(f"🗑 تم حذف `{short}` من مجموعة `{orig}`\n🔄 يرجى إعادة تشغيل السورس لتحديث الأنماط.")
    except Exception:
        await event.reply("⚠️ الاستخدام: `حذف_ربط تقييد تق`")

# =====================================================================
# 3. أمثلة على الأوامر (باستخدام الديكوريتور الجديد وبدون رموز)
# =====================================================================

@anymous_cmd('تقييد')
async def ban_handler(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"✅ تم تقييد المستخدم {reply.sender_id}")
    else:
        await event.reply("⚠️ رد على رسالة الشخص لتقييده")

@anymous_cmd('طرد')
async def kick_handler(event):
    await event.reply("🚫 تم الطرد")

# =====================================================================
# تشغيل البوت
# =====================================================================
print("🚀 Anymous Bot is Ready with Ultra-Performance Grouped Decorator...")
client.run_until_disconnected()
