from telethon import events
from ABH import *
@ABH.on(events.ChatAction)
async def on_chat_action(event):
    print(event)
    await event.reply(str(event))
