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
        "channel": "LANBOT2",  # اسم القناة بدون @
        "message_id": 52       # رقم الرسالة داخل القناة
    }
]

# دالة تطبيع النص العربي
def normalize_arabic(text):
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")
    return text.strip()

@client.on(events.NewMessage(pattern='/quiz'))
async def send_quiz(event):
    question = football[0]

    # تحميل الرسالة التي تحتوي على الصورة من القناة
    try:
        msg = await client.get_messages(question['channel'], ids=question['message_id'])
    except Exception as e:
        await event.respond("❌ حدث خطأ أثناء تحميل الصورة.")
        return

    if not msg or not msg.media:
        await event.respond("❌ لم أتمكن من العثور على الوسائط.")
        return

    # إرسال الصورة للمستخدم
    await client.send_file(
        event.chat_id,
        file=msg.media,
        caption=question['caption']
    )

    # انتظار الإجابة
    try:
        response = await client.wait_for(
            events.NewMessage(
                chats=event.chat_id,
                from_users=event.sender_id
            ),
            timeout=30
        )
    except asyncio.TimeoutError:
        await event.respond("⌛ انتهى الوقت، ما جاوبت.")
        return

    user_answer = normalize_arabic(response.text)
    correct_answer = normalize_arabic(question['answer'])

    if user_answer == correct_answer:
        await response.reply("✅ إجابة صحيحة!")
    else:
        await response.reply(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")

client.run_until_disconnected()
