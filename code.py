from telethon import events
import redis
import re
from ABH import ABH as client
from Resources import * 

# 1. دالة تسجيل الأوامر الذكية (Smart Register)
# هذه الدالة ستحل محل @client.on في أوامرك الـ 140
def anymous_cmd(command_name, **kwargs):
    def decorator(f):
        # جلب كل الاختصارات المرتبطة بهذا الأمر من Redis
        # نقوم بتنظيف اسم الأمر من الرموز للبحث في Redis
        clean_name = command_name.lstrip('/.! ')
        
        # جلب الاختصارات المخزنة (نفترض أنها مخزنة كـ Alias:Original في Redis)
        all_aliases = r.hgetall("bot_aliases")
        
        # بناء قائمة الأنماط (Pattern List)
        # نبدأ بالأمر الأصلي (مثلاً /تقييد)
        patterns = [command_name]
        
        # إضافة أي اختصار مرتبط بهذا الأمر من Redis
        if all_aliases:
            for alias, original in all_aliases.items():
                if original == clean_name:
                    # إضافة الاختصار مع دعم الـ Prefixes (/, ., !)
                    patterns.append(f"/{alias}")
                    patterns.append(f"\\.{alias}")
                    patterns.append(f"!{alias}")

        # بناء Regex واحد يجمع الكل: ^(/تقييد|/تق|\.تق|!تق)
        combined_pattern = f"^({'|'.join(patterns)})"
        
        # تسجيل الأمر في Telethon بشكل رسمي
        @client.on(events.NewMessage(pattern=combined_pattern, **kwargs))
        async def wrapper(event):
            # نمرر الحدث للدالة الأصلية
            await f(event)
        
        return f
    return decorator

# --- 2. كيفية استخدامها في الـ 140 أمر لديك ---
# بدلاً من @client.on(events.NewMessage(pattern='/تقييد'))
# استخدمها بهذا الشكل البسيط:

@anymous_cmd('/تقييد')
async def ban_handler(event):
    # الكود الخاص بك كما هو بدون أي تغيير
    if event.is_reply:
        reply = await event.get_reply_message()
        await event.reply(f"✅ تم تقييد المستخدم {reply.sender_id}")
    else:
        await event.reply("⚠️ يرجى الرد على رسالة المستخدم لتقييده.")

@anymous_cmd('/طرد')
async def kick_handler(event):
    await event.reply("🚫 تم الطرد!")

# --- 3. أمر التحكم لإضافة اختصارات جديدة (للمطور فقط) ---
@client.on(events.NewMessage(pattern=r'/ربط (.*)'))
async def add_alias(event):
    if event.sender_id != OWNER_ID: return
    
    try:
        data = event.pattern_match.group(1).split()
        original = data[0].replace('/', '')
        short = data[1].replace('/', '')
        
        # تخزين في Redis
        r.hset("bot_aliases", short, original)
        
        await event.reply(f"✅ تم ربط `{short}` بـ `{original}`\n⚠️ يرجى إعادة تشغيل السورس (Restart) لتفعيل الاختصار.")
    except:
        await event.reply("الاستخدام: `/ربط تقييد تق`")

print("Anymous Bot is Ready with Smart Decorator...")
