from ABH import *
from telethon import events
@ABH.on(events.NewMessage)
async def handle_commands(e):
    print(e)
    media = e.media
    if media:
        return await e.reply('x')
