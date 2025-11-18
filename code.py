from telethon.tl.functions.channels import GetFullChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import UpdateChannelParticipant
from telethon import events
from Resources import *
from ABH import ABH as client
import asyncio
# run.py
from telethon import TelegramClient, events
import sys
import os

# ------------------ دوال أمثلة ------------------
# أي دالة تضيفها هنا تصبح أمر تلقائي
async def تيست(e, args):
    await e.reply(f"✅ دالة تيست تعمل، والمعاملات: {args}")

async def مرحبا(e, args):
    await e.reply("أهلاً وسهلاً بك ❤️")

async def حساب(e, args):
    try:
        result = eval(args)
        await e.reply(f"نتيجة الحساب: {result}")
    except Exception as ex:
        await e.reply(f"❌ خطأ في الحساب: {ex}")

async def صورة(e, args):
    await e.reply("😂 هذه دالة تجريبية لإرسال صورة")

# ------------------ نظام تنفيذ الأوامر الذكي ------------------
@client.on(events.NewMessage)
async def executor(e):
    text = e.text.strip()
    if not text:
        return

    parts = text.split(maxsplit=1)
    cmd = parts[0]               # اسم الأمر
    args = parts[1] if len(parts) > 1 else ""  # باقي النص

    module = sys.modules[__name__]

    if hasattr(module, cmd):
        func = getattr(module, cmd)
        if callable(func):
            await func(e, args)
            return

    # إذا لم توجد الدالة
    await e.reply("❌ هذا الأمر غير موجود في النظام")

# ------------------ تشغيل البوت ------------------
print("✅ البوت شغّال...")
