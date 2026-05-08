import re, asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# =====================================================================
# 1. الديكوريتور الديناميكي (التفعيل الفوري بدون ريستارت)
# =====================================================================
def anymous_cmd(main_name, **kwargs):
    def decorator(f):
        # النمط هنا يسمح بمرور أي كلمة (نص) لكي نفحصها داخلياً
        # ^(\S+) تعني أول كلمة في الرسالة مهما كانت
        @client.on(events.NewMessage(pattern=r'^(\S+)', **kwargs))
        async def wrapper(event):
            trigger = event.pattern_match.group(1).lower()
            
            # الفحص المباشر في Redis: هل هذا الـ trigger ينتمي لمجموعة هذا الأمر؟
            # SISMEMBER هي أسرع عملية في Redis للتأكد من وجود عنصر (O(1))
            is_alias = r.sismember(f"cmd:{main_name}", trigger)
            
            # إذا كانت الكلمة هي الاسم الأصلي أو أحد الاختصارات المسجلة
            if trigger == main_name.lower() or is_alias:
                # تشغيل الدالة الأصلية في Task منفصل للأداء العالي
                asyncio.create_task(f(event))
                
        return f
    return decorator


@client.on(events.NewMessage(pattern=r'^ربط (\S+) (\S+)'))
async def add_alias(event):
    try:
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1))
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        # التخزين في Redis
        r.sadd(f"cmd:{orig}", short)
        await event.reply(f"✅ تم الربط: `{short}` ➜ `{orig}`\n🚀 التفعيل فوري الآن بدون ريستارت!")
    except: pass

@client.on(events.NewMessage(pattern=r'^حذف_ربط (\S+) (\S+)'))
async def remove_alias(event):
    try:
        orig = re.sub(r'[/.! ]', '', event.pattern_match.group(1))
        short = re.sub(r'[/.! ]', '', event.pattern_match.group(2)).lower()
        
        r.srem(f"cmd:{orig}", short)
        await event.reply(f"🗑 تم الحذف الفوري للاختصار `{short}`")
    except: pass

# =====================================================================
# 3. الأوامر (ستتعرف على الاختصارات الجديدة لحظياً)
# =====================================================================


@anymous_cmd("^(تقييد عام|مخفي قيد[هة])(?:\s+(@\w+|\d{5,10}|\d{1,5}))?(?:\s+(\d{5,10}|\d{2,4}))?$")
async def ban_handler(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"✅ تم التقييد الفوري لـ {reply.sender_id}")
    else:
        await event.reply("⚠️ رد على الرسالة")

@anymous_cmd('طرد')
async def kick_handler(event):
    await event.reply("🚫 تم الطرد")
