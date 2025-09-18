from telethon import events
from ABH import ABH
from telethon.tl.types import (
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaPoll, MessageExtendedMedia,
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    DocumentAttributeVideo, DocumentAttributeAnimated
)

# ----------------- قاعدة البيانات في الذاكرة -----------------
chat_data = {}  # {chat_id: {user_id: {type: count}}}

# ----------------- تحديد نوع الرسالة -----------------
def get_message_type(msg: Message) -> str:
    if msg is None:
        return "unknown"

    # نصوص
    if msg.message and not msg.media:
        return "text"

    # MessageExtendedMedia / Preview
    if isinstance(msg.media, MessageExtendedMediaPreview) or isinstance(msg.media, MessageExtendedMedia):
        inner = msg.media.media
        return get_message_type(Message(id=msg.id, media=inner))

    # الصور
    if isinstance(msg.media, MessageMediaPhoto):
        return "photo"

    # المستندات والفيديو/صوت/ملصق/GIF
    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""

        # أي ملصق → sticker
        if any(isinstance(attr, DocumentAttributeSticker) for attr in msg.media.document.attributes):
            return "sticker"

        for attr in msg.media.document.attributes:
            # صوت أو فويس نوت
            if isinstance(attr, DocumentAttributeAudio):
                if getattr(attr, "voice", False):
                    return "voice"  # فلتر فويس
                else:
                    return "audio"  # فلتر audio

            # فيديو عادي
            if isinstance(attr, DocumentAttributeVideo):
                return "video"  # فلتر فيديو للفيديو بصوت
            if getattr(attr, "round_message", False):
                return "voice note"  # فلتر voice note
            has_audio = getattr(attr, "audio", None) is not None
            if not has_audio:
                return "v"  # فلتر GIF للفيديو بدون صوت
            return "video"  # فلتر فيديو للفيديو بصوت

        # رسوم متحركة
        if isinstance(attr, DocumentAttributeAnimated):
            return "gif"  # فلتر GIF

        # fallback حسب MIME
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("audio/"):
            return "audio"
        return "document"

    # المواقع والأماكن والاستطلاعات
    if isinstance(msg.media, MessageMediaGeo):
        return "location"
    if isinstance(msg.media, MessageMediaVenue):
        return "venue"
    if isinstance(msg.media, MessageMediaPoll):
        return "poll"

    return "unknown"

# ----------------- تحديث الإحصائيات في الذاكرة -----------------
def update_stats(e, msg_type):
    chat = e.chat_id
    user = e.sender_id

    if chat not in chat_data:
        chat_data[chat] = {}
    if user not in chat_data[chat]:
        chat_data[chat][user] = {}

    if msg_type not in chat_data[chat][user]:
        chat_data[chat][user][msg_type] = 0

    chat_data[chat][user][msg_type] += 1
    return chat_data[chat][user]  # إرجاع إحصائيات المستخدم

# ----------------- الحدث الرئيسي للبوت -----------------
@ABH.on(events.NewMessage)
async def track_messages(e):
    m = e.message
    msg_type = get_message_type(m)

    user_stats = update_stats(e, msg_type)  
    await e.reply(f"{user_stats}")

    stats_str = "\n".join(f"{k}: {v}" for k, v in user_stats.items())
    await e.reply(f"إحصائياتك الحالية:\n{stats_str}")
