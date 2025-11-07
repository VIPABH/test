from telethon import events
from ABH import *
@ABH.on(events.ChatAction)
async def on_chat_action(event):
    if event.user_joined and event.user_added:
        await event.reply("دخول")
    elif event.user_added:
        await event.reply("إضافة")
