from telethon import events
from telethon.tl.types import DocumentAttributeAudio
from Resources import *
from ABH import *

NEW_PERFORMER = "Anymous"


@ABH.on(events.NewMessage)
@timer
async def _(e):
    if not e.media:
        return

    duration = 0
    title = None
    doc = e.document
    if doc:
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                duration = attr.duration
                title = attr.title
                break

    await ABH.send_file(
        e.chat_id,
        file=e.media,
        reply_to=e.id,
        attributes=[
            DocumentAttributeAudio(
                duration=duration,
                title=title,
                performer=NEW_PERFORMER,
            )
        ],
    )
