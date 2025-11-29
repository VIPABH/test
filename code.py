from telethon import events
from Resources import *
from ABH import ABH
messages_cache = {}
@ABH.on(events.MessageDeleted)
async def handler(event):
    print(event)
