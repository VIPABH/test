import re
import asyncio
from telethon import events
from ABH import ABH as client
from Resources import * 
OWNER_ID = wfffp
# --- 1. إعدادات القواميس ---
BOT_COMMANDS_MAP = {}
# تأكد من وضع الأيدي الصحيح هنا أو جلبها من Resources
# OWNER_ID = 12345678 

import os

def sync_commands_to_map():
    """
    تقوم بمسح ملفات المشروع (أوامر السورس) واستخراج الـ pattern يدوياً من الكود.
    """
    global BOT_COMMANDS_MAP
    BOT_COMMANDS_MAP.clear()
    
    # حدد مسار المجلد الذي يحتوي على ملفات الأوامر
    # إذا كانت الملفات في نفس المجلد، اتركها "."
    plugins_folder = "./plugins" 
    
    # Regex للبحث عن نمط: pattern=r'^/كلمة' أو pattern='/كلمة'
    # هذا النمط يسحب الكلمة التي تأتي بعد الرموز مباشرة
    pattern_regex = r"pattern\s*=\s*[r]?['\"][\^/\.!]?([آ-يa-zA-Z0-9_]+)"

    try:
        # المرور على جميع الملفات التي تنتهي بـ .py
        for root, dirs, files in os.walk(plugins_folder):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # البحث عن كل الأنماط في الملف الواحد
                        found_commands = re.findall(pattern_regex, content)
                        
                        for cmd in found_commands:
                            # نخزن اسم الأمر في القاموس
                            # ملاحظة: هنا نضع القيمة True لأننا نقوم بمسح نصي 
                            # وليس لدينا كائن الـ Handler الفعلي في هذه اللحظة
                            BOT_COMMANDS_MAP[cmd] = file_path

        print(f"✅ [File Scanner] تم مسح الملفات واكتشاف {len(BOT_COMMANDS_MAP)} أمر.")
        
    except Exception as e:
        print(f"❌ خطأ أثناء مسح الملفات: {e}")

# تعديل بسيط في أمر الربط ليتناسب مع المسح الجديد
@client.on(events.NewMessage(pattern=r'^/ربط (.*)'))
async def smart_alias_link(event):
    if event.sender_id != OWNER_ID: return
    try:
        args = event.pattern_match.group(1).split()
        original = args[0].replace('/', '').strip()
        short = args[1].replace('/', '').strip()
        
        # الربط سيتم إذا كان الأمر موجوداً في القاموس الذي ملأناه من الملفات
        if original in BOT_COMMANDS_MAP:
            r.hset("bot_aliases", short, original)
            await event.reply(f"🔗 **تم الربط بنجاح**\nالمصدر: `{BOT_COMMANDS_MAP[original]}`\nالأصل: `{original}`\nالاختصار: `{short}`")
        else:
            await event.reply(f"⚠️ الأمر `{original}` غير موجود في ملفات السورس!")
    except:
        await event.reply("⚠️ الاستخدام: `/ربط الأصل الاختصار`")
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
    # if event.sender_id != OWNER_ID: return
    sync_commands_to_map()
    count = len(BOT_COMMANDS_MAP)
    await event.reply(f"🔄 تم إعادة المسح.\nتم إيجاد `{count}` أمر في ملفات السورس.")

@client.on(events.NewMessage(pattern=r'^/الاوامر_المسجلة$'))
async def list_registered_commands(event):
    # if event.sender_id != OWNER_ID: return
    if not BOT_COMMANDS_MAP:
        return await event.reply("⚠️ القاموس فارغ. تأكد من تحميل الـ Plugins ثم أرسل /تحديث_الاوامر")

    lines = [f"• `/{cmd}`" for cmd in sorted(BOT_COMMANDS_MAP.keys())]
    header = f"📂 **الأوامر المكتشفة ({len(lines)}):**\n\n"
    
    for i in range(0, len(lines), 50):
        await event.respond(f"{header if i==0 else ''}" + "\n".join(lines[i:i+50]))


# --- 4. التشغيل التلقائي مع تأخير كافٍ ---
async def startup_process():
    # ننتظر 10 ثواني لضمان اكتمال تحميل كل موديولات البوت
    await asyncio.sleep(10)
    sync_commands_to_map()

client.loop.create_task(startup_process())
