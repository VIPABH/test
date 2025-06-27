@ABH.on(events.NewMessage)
async def reply_handler(event):
    if not event.is_group or (event.raw_text and event.raw_text.strip() in x):
        return

    sender_id = event.sender_id
    chat_id = event.chat_id
    msg_text = event.raw_text.strip() if event.raw_text else None

    if sender_id in user:
        current = user[sender_id]

        if current in ['set_reply', 'set_my_reply']:
            user[sender_id] = (current, msg_text)
            await event.reply("📩 الآن أرسل محتوى الرد (نص أو ميديا):")
            return

        elif isinstance(current, tuple):
            action, reply_name = current
            key = f"reply:{chat_id}:{reply_name}"

            if event.media:
                msg = await event.reply("📤 تم حفظ الرد كميديا.")
                file = await event.client.send_file("me", event.media, caption=f"رد محفوظ: {reply_name}")
                file_id = file.file.id if file.file else None
                rd.hset(key, mapping={
                    "type": "media",
                    "file_id": file_id
                })
            else:
                rd.hset(key, mapping={
                    "type": "text",
                    "content": msg_text
                })
                await event.reply(f'✅ تم حفظ الرد:\n• الاسم: **{reply_name}**\n• المحتوى: {msg_text}')
            del user[sender_id]
            return

        elif current == 'delete_reply':
            reply_name = msg_text
            key = f"reply:{chat_id}:{reply_name}"
            if rd.exists(key):
                rd.delete(key)
                await event.reply(f'🗑️ تم حذف الرد: **{reply_name}**')
            else:
                await event.reply(f'🚫 لا يوجد رد بهذا الاسم: **{reply_name}**')
            del user[sender_id]
            return

    # رد تلقائي
    if not msg_text:
        return

    for key in rd.scan_iter(f"reply:{chat_id}:*"):
        reply_name = key.split(f"reply:{chat_id}:")[1]
        if msg_text.startswith(reply_name):  # مطابقة عادية
            typ = rd.hget(key, "type")
            if typ == "text":
                await event.reply(rd.hget(key, "content"))
            elif typ == "media":
                file_id = rd.hget(key, "file_id")
                await event.respond(file=file_id)
            break
        elif reply_name in msg_text:  # مطابقة مميزة (كلمة داخل الجملة)
            typ = rd.hget(key, "type")
            if typ == "text":
                await event.reply(rd.hget(key, "content"))
            elif typ == "media":
                file_id = rd.hget(key, "file_id")
                await event.respond(file=file_id)
            break
