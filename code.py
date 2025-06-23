from telethon.tl.custom import Conversation
from telethon import events
from ABH import ABH, r
import json, os
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
@ABH.on(events.NewMessage(pattern=r'^/ردودي$'))
async def list_replies(event):
    sender_id = event.sender_id
    key = f"user_replies:{sender_id}"
    replies = r.lrange(key, 0, -1)
    if not replies:
        await event.reply("📭 لا توجد أي ردود محفوظة.")
        return
    message = "🗂️ قائمة ردودك:\n"
    for reply_json in replies:
        reply = json.loads(reply_json)
        name = reply['name']
        match_type = "مميز" if reply['match_type'] == "contains" else "عادي"
        message += f"• {name} — {match_type}\n"
    await event.reply(message)
@ABH.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    sender_id = event.sender_id
    key = f"user_replies:{sender_id}"
    replies = r.lrange(key, 0, -1)
    message_text = event.raw_text.strip()
    for reply_json in replies:
        reply = json.loads(reply_json)
        name = reply['name']
        match_type = reply['match_type']
        matched = (
            message_text.startswith(name) if match_type == "starts"
            else name in message_text
        )
        if matched:
            if reply['type'] == "text":
                await event.reply(reply['content'])
            elif reply['type'] == "media" and os.path.exists(reply['content']):
                await event.reply(file=reply['content'])
            return
