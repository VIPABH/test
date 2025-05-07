from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os
import asyncio
import re

# إعدادات الدخول
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# قاعدة البيانات للأسئلة
football = [
    {
        "answer": "الميعوف",
        "caption": "شنو اسم الاعب ؟",
        "photo": "https://t.me/LANBOT2/52"
    }
]

# دالة إزالة التشكيل والهمزات والفراغات الزائدة
def normalize_arabic(text):
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)  # إزالة التشكيل
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه")  # حسب الحاجة
    return text.strip()

# أمر /quiz
@client.on(events.NewMessage(pattern='/quiz'))
async def send_quiz(event):
    question = football[0]

    # إرسال الصورة والسؤال
    await client.send_file(
        event.chat_id,
        file=question['photo'],
        caption=question['caption']
    )

    try:
        # الانتظار للإجابة من نفس المستخدم خلال 30 ثانية
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

    # تطبيع الإجابة ومقارنتها
    user_answer = normalize_arabic(response.text)
    correct_answer = normalize_arabic(question['answer'])

    if user_answer == correct_answer:
        await response.reply("✅ إجابة صحيحة!")
    else:
        await response.reply(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")

client.run_until_disconnected()
