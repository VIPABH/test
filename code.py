from telethon import events
import redis
import re
from ABH import ABH as client
from Resources import * 

# --- 1. الديكوريتور الذكي (بدون رموز) ---
def anymous_cmd(command_name, **kwargs):
    def decorator(f):
        # تنظيف اسم الأمر من أي رموز تماماً
        clean_name = re.sub(r'[/.! ]', '', command_name)
        
        # جلب الاختصارات من Redis
        all_aliases = r.hgetall("bot_aliases")
        
        # قائمة الأنماط تبدأ بالأمر الخام
        patterns = [clean_name]         
        
        if all_aliases:
            for alias, original in all_aliases.items():
                # تنظيف الأصل المسجل في Redis للمقارنة
                clean_original = re.sub(r'[/.! ]', '', original)
                if clean_original == clean_name:
                    # إضافة الاختصار ككلمة خام
                    patterns.append(re.sub(r'[/.! ]', '', alias))
        
        # النمط الآن يبدأ من بداية النص ويقبل الكلمة مباشرة
        # ^(كلمة1|كلمة2)(\s+|$) لضمان عدم تداخل الكلمات (مثلاً 'تق' لا تشغل 'تقييد')
        combined_pattern = f"^({'|'.join(patterns)})(\s+|$)"
        
        @client.on(events.NewMessage(pattern=combined_pattern, **kwargs))
        async def wrapper(event):
            await f(event)
        return f
    return decorator

# --- 2. أمثلة الأوامر (تكتب الكلمة مباشرة) ---

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

@client.on(events.NewMessage(pattern=r'^ربط (.*)'))
async def add_alias(event):
    try:
        # الاستخدام: ربط تقييد تق
        data = event.pattern_match.group(1).split()
        original = re.sub(r'[/.! ]', '', data[0])
        short = re.sub(r'[/.! ]', '', data[1])
        
        r.hset("bot_aliases", short, original)
        
        await event.reply(
            f"تم ربط {short} بـ {original}\n"
            f"سوي ريستارت حتى يشتغل"
        )
    except:
        await event.reply("الاستخدام: ربط تقييد تق")

print("Anymous Bot is Ready (No Symbols Mode)...")
client.run_until_disconnected()
