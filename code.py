from ABH import *
from telethon.tl.types import InputDocument
@ABH.on(events.NewMessage)
async def x(event):
    input_doc = InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference
    )
    await ABH.send_file(chat_id, file=input_doc)
