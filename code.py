import os
from telethon import events
from telethon.tl.types import (
    DocumentAttributeAudio,
    InputDocument,
)
from Resources import *
from ABH import *


THUMB_PATH = "موارد/photo_2025-02-10_11-40-17.jpg"
NEW_PERFORMER = "Anymous"

_cached_thumb = None


async def _get_thumb_file(client):
    """رفع الصورة المصغرة مرة واحدة وإعادة استخدامها"""
    global _cached_thumb
    if _cached_thumb is not None:
        return _cached_thumb
    if os.path.exists(THUMB_PATH):
        _cached_thumb = await client.upload_file(THUMB_PATH)
    return _cached_thumb


def _is_audio_message(message) -> bool:
    """التحقق من أن الرسالة تحتوي على ملف صوتي"""
    if message.audio or message.voice:
        return True
    doc = message.document
    return bool(doc and doc.mime_type and doc.mime_type.startswith("audio/"))


def _build_updated_attributes(doc):
    """تحديث المؤدي فقط مع إبقاء العنوان والمدة والموجة وباقي الخصائص كما هي"""
    updated_attrs = []
    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
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
    return updated_attrs


def _to_input_document(doc):
    """تحويل Document إلى InputDocument"""
    return InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference,
    )


@ABH.on(events.NewMessage())
@timer
async def auto_update_incoming_audio(event):
    """التقاط الصوتيات الواردة تلقائياً وتحديث الصورة والمؤدي فقط"""
    msg = event.message
    if not _is_audio_message(msg) or not msg.document:
        return

    thumb = await _get_thumb_file(ABH)
    updated_attrs = _build_updated_attributes(msg.document)
    input_doc = _to_input_document(msg.document)

    try:
        await ABH.edit_message(
            entity=event.chat_id,
            message=msg.id,
            text=msg.text or "",
            file=input_doc,
            thumb=thumb,
            attributes=updated_attrs,
        )
    except Exception:
        await ABH.send_file(
            entity=event.chat_id,
            file=input_doc,
            caption=msg.text or "",
            attributes=updated_attrs,
            thumb=thumb,
            reply_to=msg.reply_to_msg_id,
        )
