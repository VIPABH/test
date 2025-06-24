from telethon import events
from Resources import mention
from ABH import ABH, r
import json, os
@ABH.on(events.NewMessage(pattern="^وضع ردي$"))
async def save_personal_reply(event):
    if not event.is_group:
        return await event.reply(" يجب استخدام هذا الأمر داخل مجموعة.")
    chat_id = event.chat_id
    source_type = "user"
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("📥 أرسل اسم الرد:")
        name = (await conv.get_response()).text.strip()
        key = f"group_replies:{chat_id}"
        existing_replies = r.lrange(key, 0, -1)
        for reply_json in existing_replies:
            reply = json.loads(reply_json)
            if reply["name"] == name:
                return await conv.send_message(f"⚠️ يوجد رد محفوظ مسبقًا بهذا الاسم: **{name}**")
        reply_data = {
            "name": name,
            "match_type": "starts",
            "source": source_type,
            "type": "text",
            "content": await mention(event)  # هذا هو المطلوب
        }

        r.rpush(key, json.dumps(reply_data))

        await conv.send_message(f"✅ تم حفظ الرد الخاص بك:\n• الاسم: **{name}**\n• المحتوى: {reply_data['content']}")

@ABH.on(events.NewMessage(pattern="^وضع رد$"))
async def save_reply(event):
    if not event.is_group:
        return await event.reply("❌ يجب استخدام هذا الأمر داخل مجموعة.")

    chat_id = event.chat_id
    source_type = "user" if "ردي" in event.raw_text else "group"

    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("📥 أرسل اسم الرد:")
        name = (await conv.get_response()).text.strip()

        key = f"group_replies:{chat_id}"
        existing_replies = r.lrange(key, 0, -1)
        for reply_json in existing_replies:
            reply = json.loads(reply_json)
            if reply["name"] == name:
                return await conv.send_message(f"⚠️ يوجد رد محفوظ مسبقًا بهذا الاسم: **{name}**")

        if source_type == "group":
            await conv.send_message("🔢 حدد نوع الرد:\n1️⃣ مميز (يحتوي على الكلمة)\n2️⃣ عادي (يبدأ بالكلمة)")
            match_type_response = await conv.get_response()
            match_type = "contains" if match_type_response.text.strip() == "1" else "starts"
        else:
            match_type = "starts"  # الردود الشخصية تكون عادية فقط

        await conv.send_message("📩 أرسل محتوى الرد (نص، صورة، فيديو، ملف، صوت):")
        content_response = await conv.get_response()

        reply_data = {
            "name": name,
            "match_type": match_type,
            "source": source_type,
        }

        if content_response.media:
            os.makedirs("media", exist_ok=True)
            path = await content_response.download_media(file=f"media/{chat_id}_{name}")
            reply_data["type"] = "media"
            reply_data["content"] = path
        else:
            reply_data["type"] = "text"
            reply_data["content"] = content_response.text

        r.rpush(key, json.dumps(reply_data))

        source_txt = "رد عام" if source_type == "group" else "رد خاص بك"
        await conv.send_message(f"✅ تم حفظ {source_txt}:\n• الاسم: **{name}**\n• النوع: **{'مميز' if match_type=='contains' else 'عادي'}**")

@ABH.on(events.NewMessage(pattern=r'^ردود|/replys'))
async def list_replies(event):
    if not event.is_group:
        return await event.reply("❌ هذا الأمر يعمل فقط داخل المجموعات.")

    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    replies = r.lrange(key, 0, -1)

    if not replies:
        return await event.reply("📭 لا توجد ردود محفوظة في هذه المجموعة.")

    message = "📋 **قائمة الردود المحفوظة:**\n\n"

    match_types = {"contains": "مميز", "starts": "عادي"}
    source_types = {"group": "🔵 عام", "user": "🟢 خاص"}
    content_types = {"text": "📄 نص", "media": "🖼️ ميديا"}

    for index, reply_str in enumerate(replies, start=1):
        try:
            # نقوم بتقسيم السطر إلى عناصر
            parts = reply_str.split('|')
            if len(parts) < 5:
                continue  # تجاهل الإدخالات التالفة

            name, match_type_raw, source_raw, type_raw, _ = parts

            match_type = match_types.get(match_type_raw, "❓")
            source_type = source_types.get(source_raw, "❓")
            content_type = content_types.get(type_raw, "❓")

            message += (
                f"▫️ `{index}` — **{name}**\n"
                f"   • النوع: `{match_type}`\n"
                f"   • المحتوى: {content_type}\n"
                f"   • المصدر: {source_type}\n\n"
            )
        except Exception:
            continue  # الأمان من الأخطاء

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
    async with ABH.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("🗑️ أرسل اسم الرد الذي تريد حذفه:")
        name = (await conv.get_response()).text.strip()

        key = f"group_replies:{chat_id}"
        replies = r.lrange(key, 0, -1)

        for reply_json in replies:
            reply = json.loads(reply_json)
            if reply['name'] == name:
                r.lrem(key, 0, reply_json)
                return await conv.send_message(f"✅ تم حذف الرد: **{name}**")

        await conv.send_message(f"❌ لم يتم العثور على رد بالاسم: **{name}**")

@ABH.on(events.NewMessage(pattern="^حذف ردود$"))
async def delete_all_replies(event):
    if not event.is_group:
        return
    chat_id = event.chat_id
    key = f"group_replies:{chat_id}"
    r.delete(key)
    await event.reply("🗑️ تم حذف جميع الردود في هذه المجموعة.")
