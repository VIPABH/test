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
    if msg.message and not msg.media:
        return "text"
    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"
    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                if attr.voice:
                    return "voice"
                else:
                    return "audio"
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
    get_message_type(m)
