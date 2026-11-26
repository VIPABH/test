import io
from telethon import events
from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeFilename,
)
from Resources import *
from ABH import *


NEW_PERFORMER = "Anymous"
CHUNK_SIZE = 512 * 1024  # 512 KB
UPLOAD_PART_KB = 512     # 512 KB


def _is_audio_message(message) -> bool:
    """التحقق من أن الرسالة تحتوي على ملف صوتي"""
    if message.audio or message.voice:
        return True
    doc = message.document
    return bool(doc and doc.mime_type and doc.mime_type.startswith("audio/"))


def _get_current_performer(doc) -> str | None:
    """جلب اسم المؤدي الحالي لتفادي تكرار الإرسال"""
    if not doc:
        return None
    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
            return attr.performer
    return None


def _get_audio_filename(doc) -> str:
    """استخراج اسم الملف أو تحديد اسم افتراضي"""
    if doc:
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                return attr.file_name
        if doc.mime_type and "/" in doc.mime_type:
            ext = doc.mime_type.split("/", 1)[1].split(";")[0].strip()
            if ext:
                return f"audio.{ext}"
    return "audio.mp3"


def _build_updated_attributes(doc) -> list:
    """تحديث المؤدي فقط مع إبقاء باقي الخصائص كما هي"""
    updated_attrs = []
    has_audio_attr = False

    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
            has_audio_attr = True
            updated_attrs.append(
                DocumentAttributeAudio(
                    duration=attr.duration,
                    voice=attr.voice,
                    title=attr.title,
                    performer=NEW_PERFORMER,
                    waveform=attr.waveform,
                )
            )
        else:
            updated_attrs.append(attr)

    if not has_audio_attr:
        updated_attrs.append(
            DocumentAttributeAudio(
                duration=0,
                voice=False,
                title=None,
                performer=NEW_PERFORMER,
            )
        )

    return updated_attrs


async def _download_audio_bytes(client, doc) -> bytes:
    """تحميل الصوت إلى الذاكرة بأجزاء كبيرة"""
    buf = io.BytesIO()
    async for chunk in client.iter_download(doc, request_size=CHUNK_SIZE):
        buf.write(chunk)
    return buf.getvalue()


@ABH.on(events.NewMessage())
@timer
async def auto_update_performer(event):
    """تحديث اسم المؤدي تلقائياً عند وصول ملف صوتي"""
    msg = event.message
    if not _is_audio_message(msg) or not msg.document:
        return

    current_performer = _get_current_performer(msg.document)
    if event.out and current_performer == NEW_PERFORMER:
        return

    raw_audio = await _download_audio_bytes(ABH, msg.document)
    if not raw_audio:
        return

    audio_stream = io.BytesIO(raw_audio)
    audio_stream.name = _get_audio_filename(msg.document)
    updated_attrs = _build_updated_attributes(msg.document)

    await ABH.send_file(
        entity=event.chat_id,
        file=audio_stream,
        caption=msg.text or "",
        attributes=updated_attrs,
        force_document=False,
        part_size_kb=UPLOAD_PART_KB,
        file_size=len(raw_audio),
        reply_to=msg.reply_to_msg_id,
    )
