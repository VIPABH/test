from telethon import events
from telethon.tl.types import InputPeerPhotoFileLocation
import asyncio, os
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


football = [
    {
        "answer": "الميعوف",
        "caption": "شنو اسم الاعب ؟",
        "photo": "https://t.me/LANBOT2/52"
    }
]

@client.on(events.NewMessage(pattern='/quiz'))
async def send_quiz(event):
    question = football[0]
    
    # إرسال الصورة والسؤال
    await client.send_file(
        event.chat_id,
        file=question['photo'],
        caption=question['caption']
    )
    
    # انتظار إجابة المستخدم (لمدة 30 ثانية)
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

    # التحقق من الإجابة
    if response.text.strip() == question['answer']:
        await response.reply("✅ إجابة صحيحة!")
    else:
        await response.reply(f"❌ خطأ! الجواب الصحيح هو: {question['answer']}")
