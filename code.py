from telethon import events
import random, asyncio
from ABH import ABH

@ABH.on(events.NewMessage(pattern='/num'))
async def num(event):
    if not event.is_group:
        return

    num = random.randint(1, 10)
    max_attempts = 3

    async with ABH.conversation(event.chat_id, timeout=60) as conv:
        await conv.send_message(f'اللعبة بدأت! حاول تخمين الرقم (من 1 إلى 10). لديك {max_attempts} محاولات.', file='BAADAgADE1gAAqVjsUm4S-Q8spmx2QI', reply_to=event.message.id)

        for attempt in range(1, max_attempts + 1):
            try:
                response = await conv.get_response()
                get = response.text.strip()

                try:
                    guess = int(get)
                except ValueError:
                    await conv.send_message("⚠️ يجب أن تدخل رقمًا صحيحًا فقط!")
                    continue  # تعطي فرصة أخرى

                if guess == num:
                    msg = await conv.send_message("🎉")
                    await asyncio.sleep(3)
                    await msg.edit('🎉 مُبارك! لقد فزت!')
                    return  # انتهاء اللعبة عند الفوز
                else:
                    if attempt < max_attempts:
                        await conv.send_message(f"😢 هذا ليس الرقم الصحيح. حاول مرة أخرى. المحاولة {attempt} من {max_attempts}.")
                    else:
                        msg = await conv.send_message("😢")
                        await asyncio.sleep(3)
                        await msg.edit(f'انتهت المحاولات! الرقم الصحيح هو {num}. حاول مرة أخرى لاحقًا.')
            except asyncio.TimeoutError:
                await conv.send_message('انتهى الوقت! لم تقم بإرسال إجابة في الوقت المحدد.', reply_to=event.message.id)
                return
