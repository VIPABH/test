from telethon import TelegramClient, events
import os
import asyncio
import re

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

# دالة لتنظيف النصوص العربية
def normalize_arabic(text):
    return re.sub(r'[ًٌٍَُِّْـ]', '', text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")).strip()

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

    # الانتظار لجواب المستخدم
    try:
        response = await client.wait_for(
            events.NewMessage(chats=event.chat_id, from_users=event.sender_id),
            timeout=30
        )
    except asyncio.TimeoutError:
        await event.respond("⌛ انتهى الوقت، ما جاوبت.")
        return

    # التحقق من الإجابة
    user_answer = normalize_arabic(response.text)
    correct_answer = normalize_arabic(question['answer'])

    if user_answer == correct_answer:
        await response.reply("✅ إجابة صحيحة!")
    else:
        await response.reply(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")

client.run_until_disconnected()
