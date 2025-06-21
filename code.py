from telethon import events
import random, asyncio
from ABH import ABH

@ABH.on(events.NewMessage(pattern='/num'))
async def num(event):
    if not event.is_group:
        return

    num = random.randint(1, 10)

    async with ABH.conversation(event.chat_id, timeout=60) as conv:
        await conv.send_message(f'اللعبة بدأت! حاول تخمين الرقم (من 1 إلى 10).', file='BAADAgADE1gAAqVjsUm4S-Q8spmx2QI', reply_to=event.message.id)
        try:
            response = await conv.get_response()
            get = response.text.strip()

            try:
                guess = int(get)
            except ValueError:
                await conv.send_message("⚠️ يجب أن تدخل رقمًا صحيحًا فقط!")
                return

            if guess == num:
                msg = await conv.send_message("🎉")
                await asyncio.sleep(3)
                await msg.edit('🎉 مُبارك! لقد فزت!')
            else:
                msg = await conv.send_message("😢")
                await asyncio.sleep(3)
                await msg.edit(f'للأسف، الرقم الصحيح هو {num}. حاول مرة أخرى!')
        except asyncio.TimeoutError:
            await conv.send_message('انتهى الوقت! لم تقم بإرسال إجابة في الوقت المحدد.', reply_to=event.message.id)
