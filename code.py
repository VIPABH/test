from Resources import link, hint
from telethon import events
from ABH import ABH
editsession = {}
@ABH.on(events.MessageEdited)
async def start_edit(e):
    await hint(str(await link(e)))
