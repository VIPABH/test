from telethon import events
from ABH import *
import asyncio
@ABH.on(events.ChatAction)
async def on_chat_action(event):
    await event.reply(str(event))
    me = await ABH.get_me()
    if event.user_added and event.user_id == me.id:
        await event.reply("إضافة")
