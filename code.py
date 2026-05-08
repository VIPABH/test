import re, asyncio, os, telethon.events as ev
from ABH import ABH as client
from Resources import *

MAP, OWNER_ID = {}, wfffp  # استبدل الأيدي

def sync_commands_to_map():
    global MAP
    MAP.clear()
    # مسح شامل للملفات واستخراج الأوامر بأسطر أقل
    for root, _, files in os.walk("./plugins"):
        for file in [f for f in files if f.endswith(".py")]:
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                cmds = re.findall(r"pattern\s*=\s*[r]?['\"][\^/\.!]?([آ-يa-zA-Z0-9_]+)", f.read())
                for c in cmds: MAP[c] = path
    print(f"✅ اكتمل المسح: {len(MAP)} أمر.")

# --- تعديل المحرك (Monkey Patch) ---
orig_init = ev.NewMessage.Event.__init__
def patched_init(self, *a, **k):
    if a and hasattr(a[0], 'message') and a[0].message:
        m = a[0]
        if m.message.startswith(('/', '.', '!')):
            trigger = m.message.split()[0][1:]
            real = r.hget("bot_aliases", trigger)
            if real:
                m.message = m.message.replace(trigger, real.lstrip('/.! '), 1)
                m.text = m.message
                print(f"🎯 Redirect: {trigger} -> {real}")
    orig_init(self, *a, **k)
ev.NewMessage.Event.__init__ = patched_init

# --- أوامر الإدارة ---
@client.on(ev.NewMessage(pattern=r'^/ربط (.*)'))
async def smart_alias(event):
    try:
        orig, short = event.pattern_match.group(1).split()
        r.hset("bot_aliases", short.strip('/'), orig.strip('/'))
        await event.reply(f"🔗 تم الربط: `{short}` ➜ `/{orig}`")
    except: await event.reply("⚠️ `/ربط الأصل الاختصار`")

@client.on(ev.NewMessage(pattern=r'^/(تحديث_الاوامر|الاوامر_المسجلة)'))
async def manage_cmds(event):
    if "تحديث" in event.text:
        sync_commands_to_map()
        return await event.reply(f"🔄 تم التحديث: {len(MAP)} أمر.")
    
    if not MAP: return await event.reply("⚠️ القاموس فارغ.")
    lines = [f"• `/{c}`" for c in sorted(MAP.keys())]
    for i in range(0, len(lines), 50):
        await event.respond(f"📂 **الأوامر ({len(lines)}):**\n" + "\n".join(lines[i:i+50]))

async def start_up():
    await asyncio.sleep(5)
    sync_commands_to_map()

client.loop.create_task(start_up())
