from telethon import TelegramClient, events
import json
import os
import sys
from ABH import ABH as client
# ------------------ ملف تخزين الأوامر ------------------
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

# ------------------ دوال متاحة للتنفيذ ------------------
async def تجربة(e, args):
    await e.reply(f"✅ دالة تجربة تعمل، args: {args}")

async def رفع(e, args):
    await e.reply(f"تم تنفيذ دالة رفع، args: {args}")

async def تنزيل(e, args):
    await e.reply(f"تم تنفيذ دالة تنزيل، args: {args}")

# ------------------ نظام الأوامر الذكي ------------------
@client.on(events.NewMessage)
async def executor(e):
    text = e.text.strip()
    if not text:
        return

    # تحميل الأوامر المخزنة
    cmds = load_cmds()

    parts = text.split(maxsplit=1)
    cmd = parts[0]               # الأمر أو الاختصار
    args = parts[1] if len(parts) > 1 else ""
    module = sys.modules[__name__]

    # ---- إضافة أمر مختصر من التليجرام ----
    # صيغة الرسالة: اضف امر <اختصار> <اسم_الدالة>
    if text.startswith("اضف امر"):
        try:
            _, shortcut, func_name = text.split(maxsplit=2)
        except:
            return await e.reply("❌ الصيغة الصحيحة:\nاضف امر <الاختصار> <اسم_الدالة>")

        # التحقق من وجود الدالة
        if not hasattr(module, func_name):
            return await e.reply("❌ اسم الدالة غير موجود ضمن الدوال المتاحة")

        # حفظ الاختصار
        cmds[shortcut] = func_name
        save_cmds(cmds)
        return await e.reply(f"✔️ تم ربط الاختصار `{shortcut}` بالدالة `{func_name}`")

    # ---- تنفيذ أمر مختصر ----
    if cmd in cmds:
        func_name = cmds[cmd]
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                return await func(e, args)

    # ---- الأمر غير موجود ----
    await e.reply("❌ هذا الأمر غير موجود في النظام")

# ------------------ تشغيل البوت ------------------
print("✅ البوت شغّال...")
