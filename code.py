from telethon import events
from telethon.tl.types import (
    DocumentAttributeAudio,
    InputDocument,
)
from Resources import *
from ABH import *


NEW_PERFORMER = "Anymous"


def _is_audio_message(message) -> bool:
    """التحقق من أن الرسالة تحتوي على ملف صوتي"""
    if message.audio or message.voice:
        return True
    doc = message.document
    return bool(doc and doc.mime_type and doc.mime_type.startswith("audio/"))


def _get_current_performer(doc) -> str | None:
    """جلب المؤدي الحالي لتفادي تكرار الإرسال"""
    if not doc:
        return None
    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeAudio):
            return attr.performer
    return None


def _build_updated_attributes(doc) -> list:
    """بناء قائمة الخصائص مع تحديث المؤدي فقط"""
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


def _to_input_document(doc) -> InputDocument:
    """تحويل Document إلى InputDocument بدون تحميل"""
    return InputDocument(
        id=doc.id,
        access_hash=doc.access_hash,
        file_reference=doc.file_reference,
    )


@ABH.on(events.NewMessage())
@timer
async def auto_update_performer(event):
    """إعادة إرسال الملف الصوتي فوراً بدون تحميل"""
    msg = event.message
    if not _is_audio_message(msg) or not msg.document:
        return

    if event.out and _get_current_performer(msg.document) == NEW_PERFORMER:
        return

    input_doc = _to_input_document(msg.document)
    updated_attrs = _build_updated_attributes(msg.document)

    await ABH.send_file(
        entity=event.chat_id,
        file=input_doc,
        caption=msg.text or "",
        attributes=updated_attrs,
        force_document=False,
        reply_to=msg.reply_to_msg_id,
    )
