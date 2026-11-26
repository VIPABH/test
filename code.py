import io
import os
import tempfile
from telethon import events
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename
from ABH import *
from Resources import *
NEW_PERFORMER = "Anymous"
NEW_THUMB_PATH = "موارد/photo_2025-02-10_11-40-17.jpg"  # مسار صورة مصغرة أو None إذا لم ترد تغييرها

def is_audio_message(msg) -> bool:
    doc = msg.document
    if not doc:
        return False
    if doc.mime_type and doc.mime_type.startswith("audio/"):
        return True
    return any(isinstance(attr, DocumentAttributeAudio) for attr in doc.attributes)


async def rebuild_audio_attributes(msg, new_performer: str, new_title: str | None = None):
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

@timer
@ABH.on(events.NewMessage)
async def audio_listener(e):
    if e.out or not is_audio_message(e):
        return

    attributes = await rebuild_audio_attributes(e, new_performer=NEW_PERFORMER)

    # محاولة التحميل في الذاكرة أولاً
    audio_bytes = await ABH.download_media(e.message, file=bytes)

    if audio_bytes:
        buf = io.BytesIO(audio_bytes)
        buf.name = attributes[1].file_name
        await ABH.send_file(
            e.chat_id,
            buf,
            caption=e.text or "",
            attributes=attributes,
            thumb=NEW_THUMB_PATH if NEW_THUMB_PATH and os.path.exists(NEW_THUMB_PATH) else None,
            reply_to=e.id,
        )
        return

    # بديل احتياطي عبر ملف مؤقت على القرص إذا رجع bytes قيمة None
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp_path = tmp.name

        downloaded = await ABH.download_media(e.message, file=tmp_path)
        if not downloaded:
            return

        await ABH.send_file(
            e.chat_id,
            downloaded,
            caption=e.text or "",
            attributes=attributes,
            thumb=NEW_THUMB_PATH if NEW_THUMB_PATH and os.path.exists(NEW_THUMB_PATH) else None,
            reply_to=e.id,
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
