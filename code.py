import re
import asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# --- 1. إعدادات القواميس ---
# القاموس الذي يجمع الدوال من المجلدات تلقائياً
BOT_COMMANDS_MAP = {}
OWNER_ID = wfffp

def sync_commands_to_map():
    """
    تقوم بمسح الـ Handlers المسجلة في البوت واستخراج الأوامر النصية فقط بشكل آمن.
    """
    global BOT_COMMANDS_MAP
    BOT_COMMANDS_MAP.clear()
    
    for handler, event_type in client.list_event_handlers():
        try:
            # التأكد أن الحدث هو رسالة جديدة وله نمط (pattern)
            # أضفنا فحص hasattr للتأكد أن الـ pattern موجود وليس method أو None
            if isinstance(event_type, events.NewMessage) and hasattr(event_type, 'pattern'):
                
                # التحقق أن الـ pattern هو كائن Regex وليس مجرد ميثود
                if event_type.pattern and not callable(event_type.pattern):
                    pattern_str = event_type.pattern.pattern
                    
                    # استخراج الكلمة الأساسية
                    match = re.search(r'([آ-يa-zA-Z0-9_]+)', pattern_str)
                    if match:
                        cmd_name = match.group(1)
                        BOT_COMMANDS_MAP[cmd_name] = handler
        except Exception as e:
            # تخطي أي Handler يسبب مشكلة (مثل الـ الـ Callback أو الجلسات)
            continue
    
    print(f"✅ [Discovery] تم فهرسة {len(BOT_COMMANDS_MAP)} أمر بنجاح.")
# --- 2. تعديل المحرك (Monkey Patch) ---
original_init = events.NewMessage.Event.__init__

def patched_init(self, *args, **kwargs):
    if args and hasattr(args[0], 'message'):
        msg = args[0]
        if msg.message and msg.message.startswith(('/', '.', '!')):
            prefix = msg.message[0]
            parts = msg.message.split(maxsplit=1)
            trigger = parts[0][1:]
            rest = parts[1] if len(parts) > 1 else ""

            # جلب الاسم الأصلي من Redis
            real_cmd_name = r.hget("bot_aliases", trigger)
            
            if real_cmd_name:
                clean_cmd = real_cmd_name.lstrip('/.! ')
                # تحديث نص الرسالة قبل وصولها للأوامر
                msg.message = f"{prefix}{clean_cmd} {rest}".strip()
                if hasattr(msg, 'text'):
                    msg.text = msg.message
                print(f"🎯 [Redirect] {trigger} -> {clean_cmd}")

    original_init(self, *args, **kwargs)

# تطبيق التعديل على المكتبة
events.NewMessage.Event.__init__ = patched_init

# --- 3. أوامر الإدارة والعرض ---
@client.on(events.NewMessage(pattern=r'^/ربط (.*)'))
async def smart_alias_link(event):
    if event.sender_id != OWNER_ID: return
    try:
        args = event.pattern_match.group(1).split()
        original = args[0].replace('/', '').strip()
        short = args[1].replace('/', '').strip()
        
        # التأكد أن الأمر الأصلي موجود في الفهرس
        if original in BOT_COMMANDS_MAP:
            r.hset("bot_aliases", short, original)
            await event.reply(f"🔗 **تم الربط بنجاح**\nالأصل: `{original}`\nالاختصار الجديد: `{short}`")
        else:
            await event.reply(f"⚠️ الأمر `{original}` غير موجود في ملفات البوت حالياً!")
    except:
        await event.reply("⚠️ الاستخدام: `/ربط الأصل الاختصار`")

@client.on(events.NewMessage(pattern=r'^/الاوامر_المسجلة$'))
async def list_registered_commands(event):
    if event.sender_id != OWNER_ID: return
    
    if not BOT_COMMANDS_MAP:
        return await event.reply("⚠️ القاموس فارغ، أرسل `/تحديث_الاوامر`.")

    header = f"📂 **الأوامر المكتشفة في Anymous ({len(BOT_COMMANDS_MAP)}):**\n\n"
    lines = [f"• `/{cmd}`" for cmd in sorted(BOT_COMMANDS_MAP.keys())]
    
    # تقسيم الرسائل إذا كانت القائمة طويلة (أكثر من 50 أمر لكل رسالة)
    for i in range(0, len(lines), 50):
        part = "\n".join(lines[i:i+50])
        await event.respond(f"{header if i==0 else ''}{part}")

@client.on(events.NewMessage(pattern=r'^/الاختصارات$'))
async def list_redis_aliases(event):
    if event.sender_id != OWNER_ID: return
    
    all_aliases = r.hgetall("bot_aliases")
    if not all_aliases:
        return await event.reply("⚠️ لا توجد اختصارات مسجلة.")

    msg = "🔗 **الاختصارات الحالية في Redis:**\n\n"
    for short, original in all_aliases.items():
        msg += f"• `{short}` ➜ `/{original}`\n"
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'^/تحديث_الاوامر$'))
async def refresh_map(event):
    if event.sender_id != OWNER_ID: return
    sync_commands_to_map()
    await event.reply("🔄 تم إعادة مسح ملفات السورس وتحديث القاموس.")

# --- 4. بدء التشغيل التلقائي ---
async def startup_process():
    # ننتظر قليلاً لضمان تحميل كافة الـ Plugins
    await asyncio.sleep(5)
    sync_commands_to_map()

# تشغيل المهمة في الخلفية
client.loop.create_task(startup_process())

print("🚀 Anymous Bot is running with Auto-Discovery System...")
