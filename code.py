from ABH import *
@ABH.on(events.NewMessage)
async def x(event):
    msg = event.message
    if msg.media:
        file_id = None
        if msg.photo:
            file_id = msg.photo.id
        elif msg.document:
            file_id = msg.document.id
        elif msg.video:
            file_id = msg.video.id
        else:
            file_id = None
    await event.send_file(event.chat_id, file_id)
