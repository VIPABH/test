from telethon import events
from ABH import ABH
import os
import json
from telethon.tl.types import (
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaPoll, MessageExtendedMedia,
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    DocumentAttributeVideo, DocumentAttributeAnimated
)

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
async def info(e, msg_type):
    f = 'info.json'
    if not os.path.exists(f):
        with open(f, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)

    chat = str(e.chat_id)
    user_id = str(e.sender_id)

    if chat not in data:
        data[chat] = {}
    if user_id not in data[chat]:
        data[chat][user_id] = {}

    if msg_type not in data[chat][user_id]:
        data[chat][user_id][msg_type] = 0
    data[chat][user_id][msg_type] += 1

    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return data[chat][user_id]

# ----------------- الحدث الرئيسي للبوت -----------------
@ABH.on(events.NewMessage)
async def track_messages(e):
    m = e.message
    msg_type = get_message_type(m)

    # تحديث الإحصائيات تلقائيًا لكل رسالة
    await e.reply(f"{msg_type}")
    user_stats = await info(e, msg_type)
    stats_str = json.dumps(user_stats, ensure_ascii=False, indent=2)
    await e.reply(f"إحصائياتك حتى الآن:\n{stats_str}")
