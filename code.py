import re, asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# =====================================================================
# 1. الديكوريتور الديناميكي: البحث داخل "صندوق" كل أمر بشكل منفصل
# =====================================================================
def anymous_cmd(main_name, **kwargs):
    def decorator(f):
        # النمط يسمح بمرور الكلمة الأولى فقط للفحص
        @client.on(events.NewMessage(pattern=r'^(\S+)', **kwargs))
        async def wrapper(event):
            # الكلمة اللي كتبها المستخدم (تنظيف من الرموز وتحويل لصغير)
            trigger = re.sub(r'[/.! ]', '', event.pattern_match.group(1)).lower()
            clean_main = main_name.lower()

            # 1. إذا كانت الكلمة هي نفس اسم الأمر الأصلي
            if trigger == clean_main:
                return asyncio.create_task(f(event))

            # 2. الاسترجاع من Redis حسب "مجموعة" هذا الأمر فقط
            # نتحقق هل الكلمة (trigger) موجودة داخل الـ Set الخاص بهذا الأمر
            if r.sismember(f"cmd:{clean_main}", trigger):
                return asyncio.create_task(f(event))
                
        return f
    return decorator

# =====================================================================
# 2. أوامر الإدارة: التخزين حسب المجموعة (Set)
# =====================================================================

@client.on(events.NewMessage(pattern=r'^ربط (\S+) (\S+)'))
async def add_alias(event):
    try:
        # الأصل (المجموعة) والاختصار (العنصر الجديد)
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1)).lower()
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        # التخزين في Redis: SADD تجعل الاختصار جزءاً من مجموعة "orig"
        r.sadd(f"cmd:{orig}", short)
        
        await event.reply(f"✅ تم إضافة `{short}` إلى مجموعة `{orig}`\n🚀 التفعيل فوري!")
    except:
        pass

@client.on(events.NewMessage(pattern=r'^حذف_ربط (\S+) (\S+)'))
async def remove_alias(event):
    try:
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1)).lower()
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        # حذف الاختصار من مجموعة الأمر
        r.srem(f"cmd:{orig}", short)
        await event.reply(f"🗑 تم حذف الاختصار `{short}` من مجموعة `{orig}`")
    except:
        pass

# =====================================================================
# 3. أمثلة الأوامر
# =====================================================================

@anymous_cmd('تقييد')
async def ban_handler(event):
    # كود التقييد الخاص بك
    await event.reply("تم تنفيذ أمر التقييد بنجاح ✅")

@anymous_cmd('طرد')
async def kick_handler(event):
    # كود الطرد الخاص بك
    await event.reply("تم تنفيذ أمر الطرد بنجاح 🚫")
