from ABH import ABH
from telethon import events
@ABH.on(events.NewMessage)
async def start(e):
    print(e)
