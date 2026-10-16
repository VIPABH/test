from ABH import ABH as client
import asyncio
from telethon import events
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped


call_py = PyTgCalls(client)


@client.on(events.NewMessage(pattern=r"^/join$"))
async def join_voice_call(event):
    if not event.is_group:
        await event.reply("❌ هذا الأمر يعمل داخل المجموعات فقط.")
        return

    chat_id = event.chat_id

    try:
        # في الإصدارات الحديثة، يتم الانضمام والتشغيل عبر play
        # (يجب توفير ملف صوتي مثل song.mp3 أو استخدام تدفق صوتي)
        await call_py.play(
            chat_id,
            AudioPiped("song.mp3")
        )
        await event.reply("✅ تم الانضمام إلى الاتصال الصوتي بنجاح!")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء الانضمام: {e}")


@client.on(events.NewMessage(pattern=r"^/leave$"))
async def leave_voice_call(event):
    if not event.is_group:
        return

    chat_id = event.chat_id

    try:
        # المغادرة في الإصدارات الحديثة تتم عبر leave_call
        await call_py.leave_call(chat_id)
        await event.reply("👋 تم الخروج من الاتصال الصوتي.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء المغادرة: {e}")
