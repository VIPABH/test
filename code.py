from telethon import events
import random, asyncio
from ABH import ABH
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

VIDEO_URL = 'https://t.me/VIPABH/1204'
VIDEO_KEY = 'file_id:video_game'
TARGET_USER_ID = 1910015590  # آيدي المستخدم الذي سيتم إرسال الفيديو له

async def get_or_cache_file_id():
    file_id = r.get(VIDEO_KEY)
    if file_id:
        return file_id

    # أول مرة فقط: تحميل الفيديو من الرابط وإرساله لاستخراج file_id
    file_id = VIDEO_URL.file.id
    r.set(VIDEO_KEY, file_id)

    # إرسال الفيديو إلى المستخدم المطلوب (مرة واحدة)
    await ABH.send_file(TARGET_USER_ID, file=VIDEO_URL, caption="🎬 فيديو اللعبة")

    return file_id

@ABH.on(events.NewMessage(pattern='/num'))
async def num(event):
    if not event.is_group:
        return

    number = str(random.randint(1, 10))
    file_id = await get_or_cache_file_id()

    await ABH.send_message(
        event.chat_id,
        '🎮 اللعبة بدأت! حاول تخمين الرقم (من 1 إلى 10).',
        file=file_id,
        reply_to=event.message.id
    )

    async with ABH.conversation(event.chat_id, timeout=60) as conv:
        try:
            response = await conv.get_response()
            guess = response.text.strip()

            if guess == number:
                sent = await conv.send_message("🎉")
                await asyncio.sleep(3)
                await sent.edit("🎉 مُبارك! لقد فزت!")
            else:
                sent = await conv.send_message("😢")
                await asyncio.sleep(3)
                await sent.edit(f"❌ للأسف، الرقم الصحيح هو {number}. حاول مرة أخرى!")
        except asyncio.TimeoutError:
            await conv.send_message('⏱️ انتهى الوقت! لم تقم بإرسال إجابة في الوقت المحدد.', reply_to=event.message.id)
