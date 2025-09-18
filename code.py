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
    
    if msg.message and not msg.media:
        return "text"

    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"

    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""

        for attr in msg.media.document.attributes:
            # 🎵 صوت/فويس
            if isinstance(attr, DocumentAttributeAudio):
                return "voice" if getattr(attr, "voice", False) else "audio"

            # 🏷️ ملصق
            if isinstance(attr, DocumentAttributeSticker):
                return "sticker"

            # 🎞️ فيديو
            if isinstance(attr, DocumentAttributeVideo):
                # ✅ إذا الفيديو round (مدوّر) نخليه voice note
                if getattr(attr, "round_message", False):
                    return "voice note"

                # ✅ إذا الفيديو بدون صوت → GIF
                if not getattr(attr, "supports_streaming", False) and attr.audio is None:
                    return "gif"

                return "video"

            # 🖼️ أنيميشن (Telegram GIF tgs/webm)
            if isinstance(attr, DocumentAttributeAnimated):
                return "gif"

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


@ABH.on(events.NewMessage)
async def set_my_info(e):
    m = e.message
    msg_type = get_message_type(m)
    print(f"Message type: {msg_type}")
