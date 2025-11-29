from telethon import events
from Resources import *
from ABH import ABH
@ABH.on(events.MessageEdited)
async def x(e):
    await hint(str(e))
