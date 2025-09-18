from datetime import datetime
from telethon import events
from ABH import ABH
from telethon.tl.types import (
    Message,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaGeo,
    MessageMediaVenue,
    MessageMediaPoll,
    DocumentAttributeAudio,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    DocumentAttributeAnimated
)

def get_message_type(msg: Message) -> str:
    if msg is None:
        return "unknown"

    # نص فقط
    if msg.message and not msg.media:
        return "text"

    # صورة
    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"

    # ملفات بأنواعها
    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                return "voice" if attr.voice else "audio"
            if isinstance(attr, DocumentAttributeSticker):
                return "sticker"
            if isinstance(attr, DocumentAttributeVideo):
                return "video"
            if isinstance(attr, DocumentAttributeAnimated):
                return "gif"

        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("audio/"):
            return "audio"
        else:
            return "document"

    # الموقع
    if isinstance(msg.media, MessageMediaGeo):
        return "location"

    # مكان (Venue)
    if isinstance(msg.media, MessageMediaVenue):
        return "venue"

    # استطلاع
    if isinstance(msg.media, MessageMediaPoll):
        return "poll"

    return "unknown"


@ABH.on(events.NewMessage)
async def set_my_info(e):
    m = e.message
    msg_type = get_message_type(m)
    print(f"📌 نوع الرسالة: {msg_type}")
    # تقدر ترجعها كرد مباشر إذا تحب
    # await e.reply(f"📌 نوع الرسالة: {msg_type}")
