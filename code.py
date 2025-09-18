from telethon import events
from ABH import ABH
from telethon.tl.types import (
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    MessageMediaVenue, MessageMediaPoll, MessageExtendedMedia,
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    DocumentAttributeVideo, DocumentAttributeAnimated
)
chat_data={}
def get_message_type(msg:Message)->str:
    if msg is None:
        return "unknown"
    if msg.message and not msg.media:
        return "text"
    if isinstance(msg.media,MessageExtendedMediaPreview) or isinstance(msg.media,MessageExtendedMedia):
        inner=msg.media.media
        return get_message_type(Message(id=msg.id,media=inner))
    if isinstance(msg.media,MessageMediaPhoto):
        return "photo"
    if isinstance(msg.media,MessageMediaDocument):
        mime=msg.media.document.mime_type or ""
        for attr in msg.media.document.attributes:
            if isinstance(attr,DocumentAttributeAnimated):
                return "gif"
            if isinstance(attr,DocumentAttributeSticker):
                return "sticker"
            if isinstance(attr,DocumentAttributeAudio):
                return "voice" if getattr(attr,"voice",False) else "audio"
            if isinstance(attr,DocumentAttributeVideo):
                if getattr(attr,"round_message",False):
                    return "voice note"
                return "video"
        if mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("audio/"):
            return "audio"
        return "document"
    if isinstance(msg.media,MessageMediaGeo):
        return "location"
    if isinstance(msg.media,MessageMediaVenue):
        return "venue"
    if isinstance(msg.media,MessageMediaPoll):
        return "poll"
    return "unknown"
def update_stats(e,msg_type):
    chat=e.chat_id
    user=e.sender_id
    if chat not in chat_data:
        chat_data[chat]={}
    if user not in chat_data[chat]:
        chat_data[chat][user]={}
    if msg_type not in chat_data[chat][user]:
        chat_data[chat][user][msg_type]=0
    chat_data[chat][user][msg_type]+=1
    return chat_data[chat][user]
@ABH.on(events.NewMessage)
async def track_messages(e):
    m=e.message
    msg_type=get_message_type(m)
    user_stats=update_stats(e,msg_type)
    await e.reply(f"تم تصنيف الرسالة: {msg_type}")
    stats_str="\n".join(f"{k}: {v}" for k,v in user_stats.items())
    await e.reply(f"إحصائياتك الحالية:\n{stats_str}")
