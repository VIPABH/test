import asyncio
import io
from telethon import events
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename
from Resources import *
from ABH import *

NEW_PERFORMER = "Anymous"
import asyncio
import io
from telethon import events
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename

NEW_PERFORMER = "Anymous"


def is_audio_message(msg) -> bool:
    doc = msg.document
    if not doc:
        return False
    if doc.mime_type and doc.mime_type.startswith("audio/"):
        return True
    return any(isinstance(attr, DocumentAttributeAudio) for attr in doc.attributes)


def build_audio_attributes(msg, new_performer: str, new_title: str | None = None):
    doc = msg.document
    duration = 0
    title = new_title
    is_voice = False
    waveform = None
    file_name = msg.file.name if msg.file and msg.file.name else "audio.mp3"

    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
            duration = attr.duration or 0
            is_voice = bool(attr.voice)
            waveform = attr.waveform
            if title is None:
                title = attr.title
        elif isinstance(attr, DocumentAttributeFilename):
            file_name = attr.file_name

    return [
        DocumentAttributeAudio(
            duration=duration,
            title=title,
            performer=new_performer,
            voice=is_voice,
            waveform=waveform,
        ),
        DocumentAttributeFilename(file_name=file_name),
    ]


async def process_audio(e):
    attributes = build_audio_attributes(e, new_performer=NEW_PERFORMER)
    audio_bytes = await ABH.download_media(e.message, file=bytes)
    if not audio_bytes:
        return

    buf = io.BytesIO(audio_bytes)
    buf.name = attributes[1].file_name

    await ABH.send_file(
        e.chat_id,
        buf,
        caption=e.text or "",
        attributes=attributes,
        reply_to=e.id,
    )


@ABH.on(events.NewMessage())
async def audio_listener(e):
    if e.out or not is_audio_message(e):
        return
    asyncio.create_task(process_audio(e))
