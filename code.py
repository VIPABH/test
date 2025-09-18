
from telethon import events
from Resources import info
from ABH import ABH
from telethon.tl.types import (
    Message,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaGeo,
    MessageMediaVenue,
    MessageMediaPoll,
    MessageExtendedMedia,
    MessageExtendedMediaPreview,
    MessageService,
    MessageActionTopicEdit,
    MessageActionScreenshotTaken,
    DocumentAttributeAudio,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    DocumentAttributeAnimated
)

def get_message_type(msg: Message) -> str:
    if msg is None:
        return "unknown"

    # -------------------
    # الرسائل النصية
    if msg.message and not msg.media:
        return "text"

    # -------------------
    # MessageExtendedMedia / Preview
    if isinstance(msg.media, MessageExtendedMediaPreview):
        inner = msg.media.media
        return get_message_type(Message(id=msg.id, media=inner))
    if isinstance(msg.media, MessageExtendedMedia):
        inner = msg.media.media
        return get_message_type(Message(id=msg.id, media=inner))

    # -------------------
    # الصور
    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"

    # -------------------
    # المستندات والفيديو/صوت/ملصق/GIF
    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""

        for attr in msg.media.document.attributes:
            # صوت أو فويس نوت
            if isinstance(attr, DocumentAttributeAudio):
                return "voice" if getattr(attr, "voice", False) else "audio"

            # ملصق
            if isinstance(attr, DocumentAttributeSticker):
                return "sticker"

            # فيديو
            if isinstance(attr, DocumentAttributeVideo):
                # فيديو مدوّر → Voice note
                if getattr(attr, "round_message", False):
                    return "voice note"

                # أي فيديو بدون صوت → GIF
                has_audio = getattr(attr, "audio", None) is not None
                if not has_audio:
                    return "gif"

                # الفيديو بصوت → video
                return "video"

            # GIF tgs/webm
            if isinstance(attr, DocumentAttributeAnimated):
                return "gif"

        # fallback حسب MIME
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("audio/"):
            return "audio"
        return "document"

    # -------------------
    # المواقع والأماكن والاستطلاعات
    if isinstance(msg.media, MessageMediaGeo):
        return "location"
    if isinstance(msg.media, MessageMediaVenue):
        return "venue"
    if isinstance(msg.media, MessageMediaPoll):
        return "poll"

    # -------------------
    # الرسائل النظامية
    if isinstance(msg, MessageService):
        action_type = type(msg.action).__name__
        return f"service_{action_type.lower()}"

    # -------------------
    # MessageActions محددة
    if hasattr(msg, "action"):
        if isinstance(msg.action, MessageActionTopicEdit):
            return "topic_edit"
        if isinstance(msg.action, MessageActionScreenshotTaken):
            return "screenshot_taken"

    return "unknown"


# -------------------
# البوت
@ABH.on(events.NewMessage)
async def set_my_info(e):
    m = e.message
    msg_type = get_message_type(m)
    print(f"Message type: {msg_type}")
    if m.text == 'مع':
        x, xx = await info(e, msg_type)
        await e.reply(f'{x}')
        await e.reply(f'{xx}')
