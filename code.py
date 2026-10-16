from ABH import ABH as client
import asyncio
from telethon import TelegramClient, events
from pytgcalls import PyTgCalls

call_py = PyTgCalls(client)


@client.on(events.NewMessage(pattern=r"^/join$"))
async def join_voice_call(event):
    if not event.is_group:
        await event.reply("❌ هذا الأمر يعمل داخل المجموعات فقط.")
        return

    chat_id = event.chat_id

    try:
        # الانضمام إلى الاتصال الصوتي للمجموعة
        await call_py.join_group_call(chat_id)
        await event.reply("✅ تم الانضمام إلى الاتصال الصوتي بنجاح!")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء الانضمام: {e}")


@client.on(events.NewMessage(pattern=r"^/leave$"))
async def leave_voice_call(event):
    if not event.is_group:
        return

    chat_id = event.chat_id

    try:
        # المغادرة من الاتصال الصوتي
        await call_py.leave_group_call(chat_id)
        await event.reply("👋 تم الخروج من الاتصال الصوتي.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء المغادرة: {e}")

