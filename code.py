from telethon import events, types
from ABH import *
@ABH.on(events.NewMessage)
async def handler(event):
    video = event.media.document
    file_id = video.id
    access_hash = video.access_hash
    file_reference = video.file_reference
    input_document = types.InputDocument(
        id=file_id,
        access_hash=access_hash,
        file_reference=file_reference
    )
    await ABH.send_file(
        event.chat_id,
        input_document,
        caption="تم الإرسال عبر الـ Access Hash"
    )
