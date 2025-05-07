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
        "channel": "LANBOT2",  # بدون @
        "message_id": 52
    }
]

# تطبيع النص العربي
def normalize_arabic(text):
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")
    return text.strip()

@client.on(events.NewMessage(pattern='/quiz'))
async def send_quiz(event):
    question = football[0]

    try:
        msg = await client.get_messages(question['channel'], ids=question['message_id'])
    except Exception:
        await event.respond("❌ فشل في تحميل الصورة.")
        return

    if not msg or not msg.media:
        await event.respond("❌ لا توجد صورة في الرسالة المطلوبة.")
        return

    # إرسال الصورة والسؤال
    await client.send_file(
        event.chat_id,
        file=msg.media,
        caption=question['caption']
    )

    # بدء محادثة وانتظار رد المستخدم
    try:
        async with client.conversation(event.chat_id, timeout=30) as conv:
            response = await conv.get_response()
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
