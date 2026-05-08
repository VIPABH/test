import re, asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# =====================================================================
# 1. الديكوريتور المطور (يدعم الجمل المربوطة والاختصارات الفورية)
# =====================================================================
def anymous_cmd(main_pattern, **kwargs):
    def decorator(f):
        @client.on(events.NewMessage(**kwargs))
        async def wrapper(event):
            text = event.raw_text
            if not text: return

            # 1. الفحص الأول: هل النص يطابق النمط الأصلي (Regex)؟
            if re.search(main_pattern, text):
                return asyncio.create_task(f(event))

            # 2. الفحص الثاني: فحص Redis للجمل أو الكلمات المربوطة
            # نستخرج أول كلمة أو أول جملة قبل أي مسافة
            first_word = text.split()[0].lower()
            
            # استخراج اسم المجموعة لتنظيف البحث (مثلاً "تقييد" من النمط المعقد)
            group_name = re.sub(r'[^آ-يa-zA-Z0-9]', '', main_pattern.split('|')[0]).lower()

            # التحقق من Redis (الاستجابة فورية O(1))
            if r.sismember(f"cmd:{group_name}", first_word):
                return asyncio.create_task(f(event))
                
        return f
    return decorator

# =====================================================================
# 2. أمر الربط باستخدام الاقتباس "" (يدعم المسافات)
# =====================================================================

@client.on(events.NewMessage(pattern=r'^ربط "([^"]+)" "([^"]+)"'))
async def add_alias(event):
    try:
        # استخراج ما بين الاقتباسات
        orig = event.pattern_match.group(1).strip().lower()
        short = event.pattern_match.group(2).strip().lower()
        
        # تنظيف الأصل من الرموز ليكون مفتاحاً للمجموعة
        clean_orig = re.sub(r'[/.! ]', '', orig)
        
        # التخزين في مجموعة Redis
        r.sadd(f"cmd:{clean_orig}", short)
        
        await event.reply(f"✅ تم ربط `{short}` بـ `{orig}` بنجاح!")
    except Exception as e:
        print(e)
        await event.reply("⚠️ الاستخدام: `ربط \"تقييد عام\" \"ت\"` ")

@client.on(events.NewMessage(pattern=r'^حذف_ربط "([^"]+)" "([^"]+)"'))
async def remove_alias(event):
    try:
        orig = event.pattern_match.group(1).strip().lower()
        short = event.pattern_match.group(2).strip().lower()
        clean_orig = re.sub(r'[/.! ]', '', orig)
        
        r.srem(f"cmd:{clean_orig}", short)
        await event.reply(f"🗑 تم حذف `{short}` من مجموعة `{orig}`")
    except: pass

# =====================================================================
# 3. مثال الأوامر
# =====================================================================

@anymous_cmd(r"^(تقييد عام|مخفي قيد[هة])")
async def ban_handler(event):
    await event.reply("✅ تم تنفيذ الأمر بنجاح!")
