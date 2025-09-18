from telethon import events
from Resources import info
from ABH import ABH
from telethon.tl.types import (
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    DocumentAttributeVideo, DocumentAttributeAnimated,
    MessageMediaPoll, MessageExtendedMedia,
)
def get_message_type(msg:Message)->str:
    if msg is None:
        return
    if msg.message and not msg.media:
        return "الرسائل"
    if isinstance(msg.media,MessageExtendedMediaPreview) or isinstance(msg.media,MessageExtendedMedia):
        inner=msg.media.media
        return get_message_type(Message(id=msg.id,media=inner))
    if isinstance(msg.media,MessageMediaPhoto):
        return "الصور"
    if isinstance(msg.media,MessageMediaDocument):
        for attr in msg.media.document.attributes:
            if isinstance(attr,DocumentAttributeAnimated):
                return "الgif"
        for attr in msg.media.document.attributes:
            if isinstance(attr,DocumentAttributeVideo):
                if getattr(attr,"round_message",False):
                    return "الفويس نوت"
                return "الفيديو"
        for attr in msg.media.document.attributes:
            if isinstance(attr,DocumentAttributeSticker):
                return "الستيكرات"
            if isinstance(attr,DocumentAttributeAudio):
                return "الفويسات" if getattr(attr,"voice",False) else "الصوتيات"
        mime=msg.media.document.mime_type or ""
        if mime.startswith("image/"):
            return "الصور"
        elif mime.startswith("video/"):
            return "الفيديوهات"
        elif mime.startswith("audio/"):
            return "الصوتيات"
        return "الملفات"
    if isinstance(msg.media,MessageMediaGeo):
        return "المواقع"
    if isinstance(msg.media,MessageMediaPoll):
        return "الاستفتاءات"
    return
@ABH.on(events.NewMessage)
async def track_messages(e):
    m=e.message
    msg_type=get_message_type(m)
    user_stats=await info(e,msg_type)
    await e.reply(f"تم تصنيف الرسالة: {msg_type}")
    stats_str="\n".join(f"{k}: {v}" for k,v in user_stats.items())
    await e.reply(f"إحصائياتك الحالية:\n{stats_str}")
