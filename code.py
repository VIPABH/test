from Resources import mention
from telethon import events
import random, asyncio
from ABH import ABH
@ABH.on(events.NewMessage(pattern='/num'))
async def num(event):
    if not event.is_group:
        return
    num = random.randint(1, 10)
    max_attempts = 3
    async with ABH.conversation(event.chat_id, timeout=6) as conv:
        name = mention(event)
        await conv.send_message(f'اهلا {name} تم بدء اللعبه , حاول تخمين الرقم من 10 الئ 1', file='BAADAgADE1gAAqVjsUm4S-Q8spmx2QI', reply_to=event.message.id)
        for attempt in range(1, max_attempts + 1):
            try:
                response = await conv.get_response()
                get = response.text.strip()
                try:
                    guess = int(get)
                except ValueError:
                    await conv.send_message("يابو صماخ اكتب رقم من 1 الئ 10")
                    continue
                if guess == num:
                    msg = await conv.send_message("🎉")
                    await asyncio.sleep(3)
                    await msg.edit('🎉 مُبارك! لقد فزت!')
                    return
                else:
                    if attempt < max_attempts:
                        await conv.send_message(f"جرب مرة أخرى، الرقم غلط💔")
                    else:
                        await conv.send_message(f'للأسف، لقد نفدت محاولاتك. الرقم الصحيح هو {num}')
            except asyncio.TimeoutError:
                await conv.send_message(f'انتهى الوقت! لم تقم بإرسال إجابة في الوقت المحدد. {name}', reply_to=event.message.id)
                return
