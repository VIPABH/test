from telethon import events
from telethon.tl.custom import Conversation
from ABH import ABH
from ABH import r
import json
import os

@ABH.on(events.NewMessage(pattern="^وضع رد$"))
async def save_reply(event):
    sender_id = event.sender_id
    async with ABH.conversation(sender_id, timeout=60) as conv:
        await conv.send_message("📝 أرسل اسم الرد:")
        name = (await conv.get_response()).text.strip()

        await conv.send_message("📌 حدد نوع المطابقة:\n1 - مميز (في أي مكان من الكلام)\n2 - عادي (في بداية الرسالة)")
        match_type_response = await conv.get_response()
        match_type = "contains" if match_type_response.text.strip() == "1" else "starts"

        await conv.send_message("📩 أرسل الآن محتوى الرد (نص، صورة، فيديو، ملف، صوت):")
        content_response = await conv.get_response()

        reply_data = {
            "name": name,
            "match_type": match_type,
        }

        if content_response.media:
            path = await content_response.download_media(file=f"media/{sender_id}_{name}")
            reply_data["type"] = "media"
            reply_data["content"] = path
        else:
            reply_data["type"] = "text"
            reply_data["content"] = content_response.text

        key = f"user_replies:{sender_id}"
        r.rpush(key, json.dumps(reply_data))
        await conv.send_message(f"✅ تم حفظ الرد: {name} - النوع: {'مميز' if match_type == 'contains' else 'عادي'}")
