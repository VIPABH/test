import re
import asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 

# --- 1. إعدادات القواميس ---
BOT_COMMANDS_MAP = {}
# تأكد من وضع الأيدي الصحيح هنا أو جلبها من Resources
# OWNER_ID = 12345678 

def sync_commands_to_map():
    """
    تقوم بمسح الـ Handlers المسجلة في البوت واستخراج الأوامر النصية فقط.
    """
    global BOT_COMMANDS_MAP
    BOT_COMMANDS_MAP.clear()
    
    # الحصول على قائمة المعالجات المسجلة في محرك التليثون
    handlers = client.list_event_handlers()
    
    for handler, event_type in handlers:
        try:
            # فحص دقيق للـ NewMessage التي تملك Pattern نصي
            if isinstance(event_type, events.NewMessage) and hasattr(event_type, 'pattern'):
                pattern = event_type.pattern
                
                # استخراج النص الخام من النمط سواء كان نصاً أو Regex Compiled
                if pattern:
                    pattern_str = pattern.pattern if hasattr(pattern, 'pattern') else str(pattern)
                    
                    # تنظيف النمط لاستخراج الكلمة المفتاحية (تتجاهل الرموز في البداية)
                    # يبحث عن أول كلمة نصية بعد الرموز ^ / . !
                    match = re.search(r'(?<=[\^/\.!])([آ-يa-zA-Z0-9_]+)|^[/\.!]([آ-يa-zA-Z0-9_]+)', pattern_str)
                    
                    cmd_name = None
                    if match:
                        cmd_name = match.group(1) or match.group(2)
                    
                    if cmd_name:
                        BOT_COMMANDS_MAP[cmd_name] = handler
        except:
            continue
    
    print(f"✅ [Discovery] تم اكتشاف {len(BOT_COMMANDS_MAP)} أمر في الملفات.")

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

            # فحص Redis
            real_cmd_name = r.hget("bot_aliases", trigger)
            if real_cmd_name:
                clean_cmd = real_cmd_name.lstrip('/.! ')
                msg.message = f"{prefix}{clean_cmd} {rest}".strip()
                if hasattr(msg, 'text'):
                    msg.text = msg.message
                # طباعة للتأكد في السكرين عند حدوث تحويل
                print(f"🎯 [Redirect] {trigger} -> {clean_cmd}")

    original_init(self, *args, **kwargs)

events.NewMessage.Event.__init__ = patched_init

# --- 3. أوامر الإدارة ---

@client.on(events.NewMessage(pattern=r'^/تحديث_الاوامر$'))
async def refresh_map(event):
    if event.sender_id != OWNER_ID: return
    sync_commands_to_map()
    count = len(BOT_COMMANDS_MAP)
    await event.reply(f"🔄 تم إعادة المسح.\nتم إيجاد `{count}` أمر في ملفات السورس.")

@client.on(events.NewMessage(pattern=r'^/الاوامر_المسجلة$'))
async def list_registered_commands(event):
    if event.sender_id != OWNER_ID: return
    if not BOT_COMMANDS_MAP:
        return await event.reply("⚠️ القاموس فارغ. تأكد من تحميل الـ Plugins ثم أرسل /تحديث_الاوامر")

    lines = [f"• `/{cmd}`" for cmd in sorted(BOT_COMMANDS_MAP.keys())]
    header = f"📂 **الأوامر المكتشفة ({len(lines)}):**\n\n"
    
    for i in range(0, len(lines), 50):
        await event.respond(f"{header if i==0 else ''}" + "\n".join(lines[i:i+50]))

# --- أمر الربط (معدل ليدعم الربط حتى لو لم يكتشف الأمر بعد) ---
@client.on(events.NewMessage(pattern=r'^/ربط (.*)'))
async def smart_alias_link(event):
    if event.sender_id != OWNER_ID: return
    try:
        args = event.pattern_match.group(1).split()
        original = args[0].replace('/', '').strip()
        short = args[1].replace('/', '').strip()
        
        r.hset("bot_aliases", short, original)
        status = "✅" if original in BOT_COMMANDS_MAP else "⚠️ (ملاحظة: الأمر الأصلي غير مكتشف حالياً لكن تم الربط)"
        await event.reply(f"{status} **تم الربط**\n`{short}` ➜ `/{original}`")
    except:
        await event.reply("⚠️ `/ربط الأصل الاختصار`")

# --- 4. التشغيل التلقائي مع تأخير كافٍ ---
async def startup_process():
    # ننتظر 10 ثواني لضمان اكتمال تحميل كل موديولات البوت
    await asyncio.sleep(10)
    sync_commands_to_map()

client.loop.create_task(startup_process())
