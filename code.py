from telethon import events
from ABH import ABH
import random
session = {}
x_ar = {
    't': 'تونس',
    'tt': 'تركيا',
}
@ABH.on(events.NewMessage)
async def xss(e):
    try:
        emoji, country = random.choice(list(x_ar.items()))
        g = e.chat_id
        id = e.sender_id
        t = e.text
        if g not in session or id not in session:
            session[id] = emoji, country
        if t == 'h':
            await e.reply(f'ما هو اسم العلم {emoji}')
        em = e.text
        print(em)
        country = session[id]
        print(country)
        if em == country:
            await e.reply('احسنت')
    except Exception as e:
        await e.reply(str(e))
