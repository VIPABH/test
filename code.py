from telethon import events
from Resources import mention
from ABH import ABH, r
import json, os
@ABH.on(events.NewMessage(pattern="^وضع رد$"))
async def save_reply(event):
    if not event.is_group:
        return await event.reply("يجب استخدام هذا الأمر داخل مجموعة.")
    chat_id = event.chat_id
    await event.reply("يتم وضع رد \n ارسل اكمل الرد بالخاص ```للالغاء ارسل ذ")
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("ارسل اسم الرد")
        name = (await conv.get_response()).text.strip()
        await conv.send_message("حدد نوع الرد \n ارسل 1 اذا تريده يكون مميز \n ارسل 2 اذا تريده يكون عادي")
        match_type_response = await conv.get_response()
        match_type = "contains" if match_type_response.text.strip() == "1" else "starts"
        await conv.send_message("📩 أرسل الآن محتوى الرد (نص، صورة، فيديو، ملف، صوت):")
        content_response = await conv.get_response()
        reply_data = {
            "name": name,
            "match_type": match_type,
        }
        if content_response.media:
            path = await content_response.download_media(file=f"media/{chat_id}_{name}")
            reply_data["type"] = "media"
            reply_data["content"] = path
        else:
            reply_data["type"] = "text"
            reply_data["content"] = content_response.text
        key = f"group_replies:{chat_id}"
        r.rpush(key, json.dumps(reply_data))
        await conv.send_message(f"تم وضع الرد تدلل \nاسم الرد ↢ **{name}** نوع الرد ↢ **{match_type}** ")
@ABH.on(events.NewMessage(pattern=r'^ردود|/replys'))
async def list_replies(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    replies = r.lrange(key, 0, -1)
    if not replies:
        await event.reply("📭 لا توجد أي ردود محفوظة في هذه المجموعة.")
        return
    message = " قائمة الردود في هذه المجموعة:\n"
    for index, reply_json in enumerate(replies, start=1):
        reply = json.loads(reply_json)
        name = reply['name']
        match_type = "مميز" if reply['match_type'] == "contains" else "عادي"
        message += f"{index} • {name} ⇠ {match_type}\n"
    await event.reply(message)
@ABH.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
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
@ABH.on(events.NewMessage(pattern="^حذف رد$"))
async def delete_reply(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    await event.reply("يتم حذف رد \n ارسل اسم الرد")
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        name = (await conv.get_response()).text.strip()
        key = f"group_replies:{chat_id}"
        replies = r.lrange(key, 0, -1)
        for reply_json in replies:
            reply = json.loads(reply_json)
            if reply['name'] == name:
                r.lrem(key, 0, reply_json)
                await conv.send_message(f"تم حذف الرد **{name}**")
                return
        await conv.send_message(f"لم يتم العثور على رد بالاسم **{name}**")
@ABH.on(events.NewMessage(pattern="^حذف ردود$"))
async def delete_all_replies(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    r.delete(key)
    await event.reply("تم حذف جميع الردود في هذه المجموعة.")
@ABH.on(events.NewMessage(pattern="^وضع ردي$"))
async def add_reply(event):
    if not event.is_group:
        return await event.reply("هذا الأمر يعمل في المجموعات فقط.")
    chat_id = str(event.chat_id)
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("📥 أرسل اسم الرد:")
        name = (await conv.get_response()).text.strip()
        key = f"replies:{chat_id}:{name}"
        if r.exists(key):
            return await conv.send_message(f"لا يمكنك وضع رد ب اسم **{name}**.")
        x = event.username or await mention(event)
        await r.set(key, x)
        await conv.send_message(f"تم حفظ الرد ب اسم **{name}**. ")
