from ABH import *
from Resources import *
target_bot_id = 2080276323
@ABH.on(events.NewMessage(from_users=target_bot_id))
async def _(e):
    await e.reply(str(e))
async def safe_reply_chunks(event, text):
    text = str(text)
    for i in range(0, len(text), 4000):
        await event.reply(text[i : i + 4000])
@ABH.on(events.MessageEdited(from_users=target_bot_id))
async def _(e):
    await safe_reply_chunks(e, e)
