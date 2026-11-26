import io
import os
from telethon import events
from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeFilename,
)
from Resources import *
from ABH import *


THUMB_PATH = "موارد/photo_2025-02-10_11-40-17.jpg"
NEW_PERFORMER = "Anymous"


def _is_audio_message(message) -> bool:
    """التحقق من أن الرسالة تحتوي على ملف صوتي"""
    if message.audio or message.voice:
        return True
    doc = message.document
    return bool(doc and doc.mime_type and doc.mime_type.startswith("audio/"))


def _get_current_performer(doc):
    """جلب اسم المؤدي الحالي إن وجد"""
    if not doc:
        return None
    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
            return attr.performer
    return None


def _get_audio_filename(doc) -> str:
    """استخراج اسم الملف الأصلي أو تحديد اسم افتراضي مناسب"""
    if doc:
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                return attr.file_name
        if doc.mime_type and "/" in doc.mime_type:
            ext = doc.mime_type.split("/", 1)[1].split(";")[0].strip()
            if ext:
                return f"audio.{ext}"
    return "audio.mp3"


def _build_updated_attributes(doc):
    """تحديث المؤدي فقط مع إبقاء العنوان والمدة والموجة وباقي الخصائص كما هي"""
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
    """التقاط الصوتيات الواردة تلقائياً وتحديث الصورة والمؤدي فقط"""
    msg = event.message
    if not _is_audio_message(msg) or not msg.document:
        return

    if event.out and _get_current_performer(msg.document) == NEW_PERFORMER:
        return

    audio_bytes = await ABH.download_media(msg, file=bytes)
    if not audio_bytes:
        return

    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = _get_audio_filename(msg.document)

    updated_attrs = _build_updated_attributes(msg.document)
    thumb = await ABH.upload_file(THUMB_PATH) if os.path.exists(THUMB_PATH) else None

    await ABH.send_file(
        entity=event.chat_id,
        file=audio_stream,
        caption=msg.text or "",
        attributes=updated_attrs,
        thumb=thumb,
        force_document=False,
        reply_to=msg.reply_to_msg_id,
    )
