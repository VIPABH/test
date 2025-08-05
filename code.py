from telethon import events
from Resources import x_ar
from ABH import ABH
import random
session = {}
@ABH.on(events.NewMessage)
async def xss(e):
    emoji, country = random.choice(list(x_ar.items()))
    g = e.chat_id
    id = e.sender_id
    t = e.text
    if g not in session or id not in session:
        session[id] = emoji, country
    if t == 'ا':
        await e.reply(f'ما هو اسم العلم {country}')
    em = e.text
    if em == f'{session[id]["emoji"]}':
        await e.reply('احسنت')
