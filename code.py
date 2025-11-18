from telethon import TelegramClient, events
import json
import os
import sys
import importlib
from ABH import ABH as client
# ------------------ ملف تخزين الاختصارات ------------------
CMD_FILE = "shortcuts.json"

def load_cmds():
    if not os.path.exists(CMD_FILE):
        with open(CMD_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    with open(CMD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cmds(data):
    with open(CMD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------ دوال افتراضية ------------------
async def تجربة(e, args):
    await e.reply(f"✅ دالة تجربة تعمل، args: {args}")

async def رفع(e, args):
    await e.reply(f"تم تنفيذ دالة رفع، args: {args}")

async def تنزيل(e, args):
    await e.reply(f"تم تنفيذ دالة تنزيل، args: {args}")

# ------------------ تحميل دوال ديناميكية من plugins ------------------
PLUGINS_FOLDER = "plugins"

def load_plugins():
    if not os.path.exists(PLUGINS_FOLDER):
        os.makedirs(PLUGINS_FOLDER)
    for file in os.listdir(PLUGINS_FOLDER):
        if file.endswith(".py"):
            modulename = file[:-3]
            if modulename in sys.modules:
                importlib.reload(sys.modules[modulename])
            else:
                importlib.import_module(modulename)

# ------------------ تنفيذ الأوامر ------------------
@client.on(events.NewMessage)
async def executor(e):
    text = e.text.strip()
    if not text:
        return

    # تحميل الاختصارات والدوال
    load_plugins()  # يلتقط أي دوال جديدة في plugins
    cmds = load_cmds()
    module = sys.modules[__name__]

    parts = text.split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # ---- إضافة أمر مختصر ----
    if text.startswith("اضف امر"):
        try:
            _, shortcut, func_name = text.split(maxsplit=2)
        except:
            return await e.reply("❌ الصيغة الصحيحة:\nاضف امر <الاختصار> <اسم_الدالة>")

        # تحقق من وجود الدالة في الملف الحالي أو في plugins
        if hasattr(module, func_name):
            pass
        else:
            found = False
            for f in list(sys.modules.values()):
                if hasattr(f, func_name):
                    found = True
                    break
            if not found:
                return await e.reply("❌ اسم الدالة غير موجود ضمن الدوال المتاحة")

        cmds[shortcut] = func_name
        save_cmds(cmds)
        return await e.reply(f"✔️ تم ربط الاختصار `{shortcut}` بالدالة `{func_name}`")

    # ---- تنفيذ أمر مختصر ----
    if cmd in cmds:
        func_name = cmds[cmd]
        # ابحث في الملف الحالي أو أي موديل محمّل
        func = None
        if hasattr(module, func_name):
            func = getattr(module, func_name)
        else:
            for m in list(sys.modules.values()):
                if hasattr(m, func_name):
                    func = getattr(m, func_name)
                    break
        if func and callable(func):
            return await func(e, args)

    await e.reply("❌ هذا الأمر غير موجود في النظام")

# ------------------ تشغيل البوت ------------------
print("✅ البوت شغّال...")
