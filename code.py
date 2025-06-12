from telethon import events
from telethon.tl.custom import Button
from ABH import *
@ABH.on(events.NewMessage(pattern='/start'))
async def x(event):
    async with ABH.conversation(event.chat_id) as conv:
        await conv.send_message("أرسل لي اسم القناة:")
        response = await conv.get_response()
        chanel = response.message
        await event.respond(f"تم استلام: {chanel}")
