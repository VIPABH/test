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
    
    if msg.message and not msg.media:
        return "text"

    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"

    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""

        # تحقق من الـ Attributes
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                return "voice" if getattr(attr, "voice", False) else "audio"
            if isinstance(attr, DocumentAttributeSticker):
                return "sticker"
            if isinstance(attr, DocumentAttributeAnimated):
                return "gif"   # نفصل الـ GIF عن الفيديو هنا
            if isinstance(attr, DocumentAttributeVideo):
                return "video"

        # fallback حسب الـ MIME
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("audio/"):
            return "audio"
        return "document"

    if isinstance(msg.media, MessageMediaGeo):
        return "location"
    if isinstance(msg.media, MessageMediaVenue):
        return "venue"
    if isinstance(msg.media, MessageMediaPoll):
        return "poll"

    return "unknown"


async def set_my_info(e):
    m = e.message
    msg_type = get_message_type(m)
    print(f"Message type: {msg_type}")
