from telethon import events
from ABH import ABH
import os, asyncio
@ABH.on(events.NewMessage)
async def mypic(event):
    sender = await event.get_sender()
    user = await event.client.get_entity(sender.id)
    print(sender)
    await asyncio.sleep(4)
    print(user)
