from ABH import *
from Resources import *
from telethon import events
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename

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

    audio_attr = DocumentAttributeAudio(
        duration=duration,
        title=title,
        performer=new_performer,
        voice=is_voice,
        waveform=waveform,
    )
    return [
        audio_attr,
        DocumentAttributeFilename(file_name=file_name),
    ]


@ABH.on(events.NewMessage())
async def audio_listener(e):
    # فلترة: تجاهل الرسائل التي لا تحتوي على ملف صوتي
    if not is_audio_message(e):
        return

    # أمثلة فلاتر إضافية حسب حاجتك (فعّل ما تحتاجه):
    # if not e.is_group: return
    # if e.sender_id != TARGET_USER_ID: return
    # if e.chat_id != TARGET_CHAT_ID: return

    attributes = await rebuild_audio_attributes(e, new_performer=NEW_PERFORMER)
    audio_bytes = await ABH.download_media(e, file=bytes)

    await ABH.send_file(
        e.chat_id,
        audio_bytes,
        caption=e.text or "",
        attributes=attributes,
        thumb=NEW_THUMB_PATH,
        reply_to=e.id,
    )
