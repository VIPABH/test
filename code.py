import asyncio
from hydrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# بيانات البوت أو الحساب
api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

# إعداد عميل Hydrogram (بديل Telethon)
app = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# إعداد عميل الاتصالات الصوتية
call_py = PyTgCalls(app)


@app.on_message(filters.command("join") & filters.group)
async def join_voice_call(client, message):
    chat_id = message.chat.id

    try:
        # الانضمام والتشغيل في الاتصال الصوتي
        await call_py.play(
            chat_id,
            MediaStream("song.mp3")  # تأكد من وجود ملف صوتي بهذا الاسم
        )
        await message.reply("✅ تم الانضمام إلى الاتصال الصوتي وبدء تشغيل الصوت بنجاح باستخدام Hydrogram!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء الانضمام: {e}")


@app.on_message(filters.command("leave") & filters.group)
async def leave_voice_call(client, message):
    chat_id = message.chat.id

    try:
        await call_py.leave_call(chat_id)
        await message.reply("👋 تم الخروج من الاتصال الصوتي.")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء المغادرة: {e}")


async def main():
    await call_py.start()
    print("🤖 بدأ تشغيل عميل الصوت...")
    await app.start()
    print("🚀 البوت يعمل الآن بنجاح!")
    await idle()


if __name__ == "__main__":
    from hydrogram import idle
    app.run(main())
