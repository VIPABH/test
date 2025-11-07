from telethon import events
from ABH import *
@ABH.on(events.ChatAction)
async def on_chat_action(event):
    if event.user_added and event.sender_id == await ABH.get_me().id:
        await event.reply('...')
