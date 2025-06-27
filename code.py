from Resources import mention
from telethon import events
from ABH import ABH, r
import json, os
x = ["وضع رد", "وضع ردي", "حذف رد", "حذف ردود", "ردود", "/replys"]
@ABH.on(events.NewMessage(pattern="^وضع ردي$"))
async def save_personal_reply(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("📥 أرسل اسم الرد:")
        name = (await conv.get_response()).text.strip()
        if name in x:
            return
        key = f"group_replies:{chat_id}"
        existing_replies = r.lrange(key, 0, -1)
        for reply_json in existing_replies:
            reply = json.loads(reply_json)
            if reply["name"] == name:
                return await conv.send_message(f"يوجد رد محفوظ مسبقًا بهذا الاسم: **{name}**")
        reply_data = {
            "name": name,
            "type": "نص",
            "content": await mention(event)
        }
        r.rpush(key, json.dumps(reply_data))
        await conv.send_message(f" تم حفظ الرد الخاص بك:\n• الاسم: **{name}**\n• المحتوى: {reply_data['content']}")
user_states = {}
@ABH.on(events.NewMessage(pattern="^وضع رد$"))
async def start_reply(event):
    if not event.is_group:
        return
    user_states[event.sender_id] = {"step": "name"}
    await event.reply("📥 أرسل اسم الرد:")
@ABH.on(events.NewMessage())
async def handle_reply(event):
    if not event.is_group:
        return
    state = user_states.get(event.sender_id)
    if not state:
        return
    if event.message.text in x:
        return
    if state["step"] == "name":
        state["name"] = event.raw_text.strip()
        state["step"] = "content"
        await event.reply("📩 أرسل محتوى الرد:")
    elif state["step"] == "content":
        name = state["name"]
        content = event.raw_text.strip()
        reply_data = {
            "name": name,
            "match_type": "starts",
            "source": "user",
            "type": "text",
            "content": content
        }
        key = f"group_replies:{event.chat_id}"
        r.rpush(key, json.dumps(reply_data))
        del user_states[event.sender_id]
        await event.reply(f"✅ تم حفظ الرد: **{name}**")
@ABH.on(events.NewMessage(pattern=r'^ردود|/replys'))
async def list_replies(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    replies = r.lrange(key, 0, -1)
    if not replies:
        return await event.reply("📭 لا توجد ردود محفوظة في هذه المجموعة.")
    message = "📋 **قائمة الردود المحفوظة:**\n\n"
    for index, reply_str in enumerate(replies, start=1):
        try:
            reply = json.loads(reply_str)
            name = reply.get("name", "❓")
            message += (
                f"▫️ `{index}` — **{name}**\n"
            )
        except Exception:
            continue
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
                await ABH.send_file(event.chat_id, file=reply['content'], reply_to=event.message.id)
@ABH.on(events.NewMessage(pattern="^حذف رد$"))
async def delete_reply(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("🗑️ أرسل اسم الرد الذي تريد حذفه:")
        name = (await conv.get_response()).text.strip()
        key = f"group_replies:{chat_id}"
        replies = r.lrange(key, 0, -1)
        for reply_json in replies:
            reply = json.loads(reply_json)
            if reply['name'] == name:
                r.lrem(key, 0, reply_json)
                return await conv.send_message(f" تم حذف الرد: **{name}**")
        await conv.send_message(f" لم يتم العثور على رد بالاسم: **{name}**")
@ABH.on(events.NewMessage(pattern="^حذف ردود$"))
async def delete_all_replies(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    r.delete(key)
    await event.reply("🗑️ تم حذف جميع الردود في هذه المجموعة.")
