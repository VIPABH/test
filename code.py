import io
from telethon import events
from telethon.tl.types import DocumentAttributeAudio
from Resources import *
from ABH import *

NEW_PERFORMER = "Anymous"


@ABH.on(events.NewMessage)
@timer
async def _(e):
    if not e.audio and not e.document:
        return

    duration = 0
    title = None
    doc = e.document
    if doc:
        if doc.mime_type and not doc.mime_type.startswith("audio/"):
            return
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                duration = attr.duration
                title = attr.title
                break

    buf = io.BytesIO()
    await e.download_media(file=buf)
    if buf.getbuffer().nbytes == 0:
        return
    buf.seek(0)
    buf.name = getattr(e.file, "name", None) or "audio.mp3"

    await ABH.send_file(
        e.chat_id,
        file=buf,
        reply_to=e.id,
        attributes=[
            DocumentAttributeAudio(
                duration=duration,
                title=title,
                performer=NEW_PERFORMER,
            )
        ],
    )
