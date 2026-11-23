from ABH import *
from Resources import *
target_bot_id = 2080276323
@ABH.on(events.NewMessage(from_users=target_bot_id))
async def _(e):
    await e.reply(str(e))
@ABH.on(events.MessageEdited(from_users=target_bot_id))
async def _(e):
    await e.reply(str(e))
