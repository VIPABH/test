import re, asyncio, os, telethon.events as ev
from ABH import ABH as client
from Resources import *

MAP = {}

def sync_commands_to_map():
    global MAP
    MAP.clear()
    # استخدام المسار المطلق لضمان العثور على المجلد في Ubuntu
    base_path = os.path.join(os.getcwd(), "plugins") 
    if not os.path.exists(base_path): base_path = os.getcwd() # إذا لم يجد plugins يبحث في المجلد الحالي
    
    for root, _, files in os.walk(base_path):
        for file in [f for f in files if f.endswith(".py")]:
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                # Regex مطور جداً يسحب أي نص داخل pattern= سواء كان r أو بدون
                cmds = re.findall(r"pattern\s*=\s*[r]?['\"](?:[\^/\.!])?([آ-يa-zA-Z0-9_]+)", f.read())
                for c in cmds: MAP[c] = file
    print(f"✅ تم اكتشاف: {len(MAP)} أمر.")

# --- تعديل المحرك (Monkey Patch) ---
orig_init = ev.NewMessage.Event.__init__
def patched_init(self, *a, **k):
    if a and hasattr(a[0], 'message') and a[0].message:
        m = a[0]
        if m.message.startswith(('/', '.', '!')):
            trigger = m.message.split()[0][1:]
            real = r.hget("bot_aliases", trigger)
            if real:
                # استبدال ذكي للاختصار بالأصل
                m.message = m.message.replace(trigger, real.replace('/', ''), 1)
                m.text = m.message
    orig_init(self, *a, **k)
ev.NewMessage.Event.__init__ = patched_init

# --- أوامر الإدارة ---
@client.on(ev.NewMessage(pattern=r'^/(ربط|تحديث_الاوامر|الاوامر_المسجلة)'))
async def manager(e):
    # if e.sender_id != OWNER_ID: return # فك التعليق للحماية
    txt = e.text
    if "ربط" in txt:
        try:
            _, o, s = txt.split()
            r.hset("bot_aliases", s.strip('/'), o.strip('/'))
            return await e.reply(f"🔗 تم الربط: `{s}` ➜ `{o}`")
        except: return await e.reply("⚠️ `/ربط الأصل الاختصار`")
    
    if "تحديث" in txt:
        sync_commands_to_map()
        return await e.reply(f"🔄 تم التحديث: {len(MAP)} أمر.")
    
    if not MAP: return await e.reply("⚠️ القاموس فارغ.")
    res = [f"• `/{c}`" for c in sorted(MAP.keys())]
    for i in range(0, len(res), 50):
        await e.respond(f"📂 **الأوامر ({len(res)}):**\n" + "\n".join(res[i:i+50]))

async def start_up():
    await asyncio.sleep(10) # زيادة الوقت للتأكد من استقرار السيرفر
    sync_commands_to_map()

client.loop.create_task(start_up())
