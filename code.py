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
        message_type = "unknown"
        return message_type

    if msg.message and not msg.media:
        message_type = "text"
        return message_type

    if isinstance(msg.media, MessageExtendedMediaPreview) or isinstance(msg.media, MessageExtendedMedia):
        inner = msg.media.media
        message_type = get_message_type(Message(id=msg.id, media=inner))
        return message_type

    if isinstance(msg.media, MessageMediaPhoto):
        message_type = "photo"
        return message_type

    if isinstance(msg.media, MessageMediaDocument):
        mime = msg.media.document.mime_type or ""

        # ملصق ثابت أو متحرك
        if any(isinstance(attr, DocumentAttributeSticker) for attr in msg.media.document.attributes):
            message_type = "sticker"
            return message_type

        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                message_type = "voice" if not getattr(attr, "voice", False) else "voice note"
                return message_type

            if isinstance(attr, DocumentAttributeVideo):
                if getattr(attr, "round_message", False):
                    message_type = "voice note"
                else:
                    has_audio = getattr(attr, "audio", None) is not None
                    if not has_audio:
                        message_type = "gif"
                    else:
                        message_type = "video"
                return message_type

            if isinstance(attr, DocumentAttributeAnimated):
                message_type = "gif"
                return message_type

        if mime.startswith("image/"):
            message_type = "image"
        elif mime.startswith("video/"):
            message_type = "video"
        elif mime.startswith("audio/"):
            message_type = "audio"
        else:
            message_type = "document"
        return message_type

    if isinstance(msg.media, MessageMediaGeo):
        message_type = "location"
        return message_type
    if isinstance(msg.media, MessageMediaVenue):
        message_type = "venue"
        return message_type
    if isinstance(msg.media, MessageMediaPoll):
        message_type = "poll"
        return message_type

    message_type = "unknown"
    return message_type

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

    user_stats = update_stats(e, msg_type)  # التحديث في المتغير المحلي

    # إذا أحببت، يمكن الرد بالإحصائيات الحالية
    # stats_str = "\n".join(f"{k}: {v}" for k, v in user_stats.items())
    # await e.reply(f"إحصائياتك الحالية:\n{stats_str}")
