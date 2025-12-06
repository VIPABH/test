from Resources import link, hint
from telethon import events
from ABH import ABH
editsession = {}
@ABH.on(events.MessageEdited)
async def start_edit(e):
    if getattr(e, 'edit_hide', True) or e.sender_id is None:
        return
    old_text = getattr(e, 'old_text', None)
    new_text = getattr(e, 'text', None)
    if old_text == new_text:
        return
    try:
        result = str(await link(e))
        await hint(result)
    except Exception as ex:
        print(f"Error handling edited message: {ex}")
