from ABH import *
@ABH.on(events.NewMessage)
async def x(event):
    msg = event.message
    await event.reply(f'{msg.id}')
    await ABH.send_file(event.chat_id, file=msg.id, reply_to=event.id)
