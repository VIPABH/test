import io
import os
from telethon import events
from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeFilename,
)
from mutagen.id3 import APIC, ID3, TPE1
from Resources import *
from ABH import *


THUMB_PATH = "موارد/photo_2025-02-10_11-40-17.jpg"
NEW_PERFORMER = "Anymous"
CHUNK_SIZE = 512 * 1024  # 512 KB أقصى حجم جزء في تيليجرام

_THUMB_BYTES = None


def _get_thumb_bytes() -> bytes | None:
    """قراءة الصورة مرة واحدة في الذاكرة"""
    global _THUMB_BYTES
    if _THUMB_BYTES is not None:
        return _THUMB_BYTES
    if os.path.exists(THUMB_PATH):
        with open(THUMB_PATH, "rb") as f:
            _THUMB_BYTES = f.read()
    return _THUMB_BYTES


def _is_audio_message(message) -> bool:
    """التحقق من أن الرسالة تحتوي على ملف صوتي"""
    if message.audio or message.voice:
        return True
    doc = message.document
    return bool(doc and doc.mime_type and doc.mime_type.startswith("audio/"))


def _get_current_performer(doc) -> str | None:
    """جلب المؤدي الحالي لتفادي إعادة المعالجة"""
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


async def _download_audio_fast(client, doc) -> bytes:
    """تحميل الملف الصوتي على أجزاء كبيرة مباشرة إلى الذاكرة"""
    buf = io.BytesIO()
    async for chunk in client.iter_download(doc, request_size=CHUNK_SIZE):
        buf.write(chunk)
    return buf.getvalue()


def _patch_mp3_in_memory(raw_bytes: bytes, thumb_bytes: bytes | None) -> bytes:
    """تعديل وسوم MP3 داخل الذاكرة دون كتابة ملفات على القرص"""
    buf = io.BytesIO(raw_bytes)
    try:
        tags = ID3(buf)
    except Exception:
        tags = ID3()

    tags["TPE1"] = TPE1(encoding=3, text=[NEW_PERFORMER])

    if thumb_bytes:
        tags.delall("APIC")
        tags["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=thumb_bytes,
        )

    out = io.BytesIO(raw_bytes)
    tags.save(out)
    return out.getvalue()


def _build_updated_attributes(doc) -> list:
    """تحديث المؤدي فقط مع إبقاء باقي خصائص الصوت كما هي"""
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


@ABH.on(events.NewMessage())
@timer
async def auto_update_incoming_audio(event):
    """التقاط الصوتيات وتحديث المؤدي والصورة بأسرع مسار"""
    msg = event.message
    if not _is_audio_message(msg) or not msg.document:
        return

    if event.out and _get_current_performer(msg.document) == NEW_PERFORMER:
        return

    raw_audio = await _download_audio_fast(ABH, msg.document)
    if not raw_audio:
        return

    thumb_bytes = _get_thumb_bytes()
    filename = _get_audio_filename(msg.document)

    if filename.lower().endswith(".mp3"):
        raw_audio = _patch_mp3_in_memory(raw_audio, thumb_bytes)

    audio_stream = io.BytesIO(raw_audio)
    audio_stream.name = filename

    thumb_stream = None
    if thumb_bytes:
        thumb_stream = io.BytesIO(thumb_bytes)
        thumb_stream.name = "thumb.jpg"

    updated_attrs = _build_updated_attributes(msg.document)

    await ABH.send_file(
        entity=event.chat_id,
        file=audio_stream,
        caption=msg.text or "",
        attributes=updated_attrs,
        thumb=thumb_stream,
        force_document=False,
        reply_to=msg.reply_to_msg_id,
    )
