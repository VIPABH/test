from Resources import mention
from telethon import events
from ABH import ABH, r
import json, os
import redis

# الاتصال بـ Redis
rd = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

x = ["وضع رد", "وضع ردي", "حذف رد", "حذف ردود", "ردود", "/replys"]
user = {}

@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    if not event.is_group:
        return
    await event.reply('📥 اكتب اسم الرد الذي تريد وضعه:')
    user[event.sender_id] = 'set_reply'

@ABH.on(events.NewMessage(pattern=r'^وضع ردي$'))
async def set_my_reply(event):
    if not event.is_group:
        return
    await event.reply('📥 اكتب اسم الرد الذي تريد وضعه:')
    user[event.sender_id] = 'set_my_reply'

@ABH.on(events.NewMessage(pattern='^حذف رد$'))
async def delete_reply(event):
    if not event.is_group:
        return
    await event.reply('🗑️ اكتب اسم الرد الذي تريد حذفه:')
    user[event.sender_id] = 'delete_reply'

@ABH.on(events.NewMessage(pattern='^حذف ردود$'))
async def delete_replies(event):
    if not event.is_group:
        return
    for key in rd.scan_iter("reply:*"):
        rd.delete(key)
    await event.reply('🗑️ تم حذف جميع الردود بنجاح.')

@ABH.on(events.NewMessage(pattern='^ردود$'))
async def get_replies(event):
    if not event.is_group:
        return
    keys = list(rd.scan_iter("reply:*"))
    if not keys:
        await event.reply('📭 لا توجد ردود محفوظة.')
        return
    replys_text = []
    for key in keys:
        name = key.split("reply:")[1]
        typ = rd.hget(key, "type")
        replys_text.append(f'▫️ **{name}** : {typ}')
    await event.reply('\n'.join(replys_text))

@ABH.on(events.NewMessage)
async def reply_handler(event):
    if not event.is_group or (event.raw_text and event.raw_text.strip() in x):
        return

    sender_id = event.sender_id
    msg_text = event.raw_text.strip() if event.raw_text else None

    if sender_id in user:
        current = user[sender_id]

        if current in ['set_reply', 'set_my_reply']:
            user[sender_id] = (current, msg_text)
            await event.reply("📩 الآن أرسل محتوى الرد (نص أو ميديا):")
            return

        elif isinstance(current, tuple):
            action, reply_name = current

            if event.media:
                msg = await event.reply("📤 تم حفظ الرد كميديا.")
                file = await event.client.send_file("me", event.media, caption=f"رد محفوظ: {reply_name}")
                rd.hset(f"reply:{reply_name}", mapping={
                    "type": "media",
                    "file_id": file.file.id
                })
            else:
                rd.hset(f"reply:{reply_name}", mapping={
                    "type": "text",
                    "content": msg_text
                })
                await event.reply(f'✅ تم حفظ الرد:\n• الاسم: **{reply_name}**\n• المحتوى: {msg_text}')
            del user[sender_id]
            return

        elif current == 'delete_reply':
            reply_name = msg_text
            key = f"reply:{reply_name}"
            if rd.exists(key):
                rd.delete(key)
                await event.reply(f'🗑️ تم حذف الرد: **{reply_name}**')
            else:
                await event.reply(f'🚫 لا يوجد رد بهذا الاسم: **{reply_name}**')
            del user[sender_id]
            return

    # الرد التلقائي عند التطابق
    if not msg_text:
        return

    for key in rd.scan_iter("reply:*"):
        reply_name = key.split("reply:")[1]
        if msg_text.startswith(reply_name):
            typ = rd.hget(key, "type")
            if typ == "text":
                await event.reply(rd.hget(key, "content"))
            elif typ == "media":
                file_id = rd.hget(key, "file_id")
                await event.respond(file=file_id)
            break
