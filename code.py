from Resources import link, hint
from telethon import events
from ABH import ABH
editsession = {}
@ABH.on(events.MessageEdited)
async def start_edit(e):
    if getattr(e, 'edit_hide', True):
        return
    await hint(str(await link(e)))
