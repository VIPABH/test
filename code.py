from telethon import events
from Resources import wfffp
from ABH import ABH

def is_allowed_sender(event):
    return event.sender_id == wfffp



@ABH.on(events.NewMessage(func=is_allowed_sender))
async def auto_reply(event):
    await event.reply('...')
