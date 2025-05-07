from telethon import TelegramClient, events
import os
import asyncio

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

football = [
    {
        "answer": "الميعوف",
        "caption": "شنو اسم الاعب ؟",
        "channel": "LANBOT2",
        "message_id": 52
    }
]

@client.on(events.NewMessage(pattern='/quiz'))
async def send_quiz(event):
    # جلب السؤال والجواب
    question = football[0]

    try:
        msg = await client.get_messages(question['channel'], ids=question['message_id'])
        if not msg or not msg.media:
            raise ValueError("لا توجد وسائط.")
    except Exception:
        await event.respond("❌ لم أتمكن من تحميل السؤال أو الصورة.")
        return

    # إرسال الصورة مع التسمية
    await client.send_file(event.chat_id, file=msg.media, caption=question['caption'])

    # انتظار الجواب من المستخدم
    response = await client.send_message(event.chat_id, "يرجى إرسال الإجابة!")

    # التحقق من الإجابة
    user_answer = event.text.strip()
    correct_answer = question['answer']

    if user_answer == correct_answer:
        await response.reply("✅ إجابة صحيحة!")
    else:
        await response.reply(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")

client.run_until_disconnected()
