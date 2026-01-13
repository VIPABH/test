from Resources import wfffp
from ABH import *
def x(e):
    if e.sender_id == wfffp:
        return True
@ABH.on(events.NewMessage(func=x))
async def reply(e):
    await e.reply('...')
