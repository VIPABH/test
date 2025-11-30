from telethon import events
from Resources import *
from ABH import ABH
messages_cache = {}
@ABH.on(events.NewMessage)
async def مستمع_اللطميات(e):
    text = e.text.strip()
    if text not in لطميات:
        return
    msg_id = لطميات[text]["message_id"]
    b = Button.url('❤', url=f'https://t.me/x04ou/{msg_id}')
    msgs = await ABH.get_messages('x04ou', ids=[msg_id])
    if not msgs:
        return
    msg = msgs[0]
    await ABH.send_file(e.chat_id, msg, reply_to=e.id, buttons=b)
button = [Button.inline('التالي', data=f'next'), Button.inline('السابق', data=f'retrunback')]
@ABH.on(events.NewMessage(pattern='^لطميات$', from_users=[wfffp]))
async def listlatmeat(e):
    msg = ''
    for name, data in list(لطميات.items())[:50]:
        msg += f'( `{name}` )\n'
    await chs(e, msg)
