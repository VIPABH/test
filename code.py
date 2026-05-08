import re, asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# =====================================================================
# 1. الديكوريتور المطور (يدعم الأنماط المعقدة + اختصارات Redis الفورية)
# =====================================================================
def anymous_cmd(main_pattern, **kwargs):
    def decorator(f):
        # النمط هنا يستقبل الرسالة كاملة لفحصها
        @client.on(events.NewMessage(**kwargs))
        async def wrapper(event):
            text = event.raw_text
            if not text: return

            # 1. الفحص الأول: هل النص يطابق النمط الأصلي (Regex)؟
            if re.search(main_pattern, text):
                return asyncio.create_task(f(event))

            # 2. الفحص الثاني: هل الكلمة الأولى هي اختصار مسجل في Redis؟
            # نستخرج أول كلمة فقط للبحث في Redis (مثلاً: "تق")
            first_word = text.split()[0].lower()
            first_word_clean = re.sub(r'[/.! ]', '', first_word)

            # استخراج "اسم المجموعة" من النمط الأصلي (لأغراض الربط)
            # إذا كان النمط Regex معقد، نأخذ أول كلمة منه كاسم للمجموعة
            group_name = re.sub(r'[^آ-يa-zA-Z0-9]', '', main_pattern.split('|')[0]).lower()

            if r.sismember(f"cmd:{group_name}", first_word_clean):
                return asyncio.create_task(f(event))
                
        return f
    return decorator

# =====================================================================
# 2. أوامر الإدارة (الربط الفوري)
# =====================================================================

@client.on(events.NewMessage(pattern=r'^ربط (\S+) (\S+)'))
async def add_alias(event):
    try:
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1)).lower()
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        r.sadd(f"cmd:{orig}", short)
        await event.reply(f"✅ تم ربط `{short}` بـ `{orig}` فورياً!")
    except: pass

@client.on(events.NewMessage(pattern=r'^حذف_ربط (\S+) (\S+)'))
async def remove_alias(event):
    try:
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1)).lower()
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        r.srem(f"cmd:{orig}", short)
        await event.reply(f"🗑 تم حذف الاختصار `{short}`")
    except: pass

# =====================================================================
# 3. الأوامر (دعم كامل للأنماط المعقدة)
# =====================================================================

# الآن سيعمل هذا النمط المعقد، وإذا ربطت كلمة "ق" بـ "تقييد"، ستعمل أيضاً!
@anymous_cmd(r"^(تقييد عام|مخفي قيد[هة])(?:\s+(@\w+|\d{5,10}))?")
async def ban_handler(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"✅ تم التقييد لـ {reply.sender_id}")
    else:
        await event.reply("⚠️ رد على الرسالة")

@anymous_cmd('طرد')
async def kick_handler(event):
    await event.reply("🚫 تم الطرد")
