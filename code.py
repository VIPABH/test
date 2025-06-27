import redis
from telethon import events
from ABH import ABH
from Resources import mention

r = redis.Redis(decode_responses=True)
session = {}

banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز', 'عرض الردود', 'حذف الردود']

def get_key(chat_id):
    return f"replies:{chat_id}"

@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'chat_id': chat_id, 'step': 'waiting_for_reply_name', 'type': 'normal'}

@ABH.on(events.NewMessage(pattern='^وضع رد مميز$'))
async def set_special_reply(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'chat_id': chat_id, 'step': 'waiting_for_reply_name', 'type': 'special'}

@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'chat_id': chat_id, 'step': 'waiting_for_reply_name', 'type': 'mention'}

@ABH.on(events.NewMessage(pattern='^إلغاء$'))
async def cancel_session(event):
    user_id = event.sender_id
    if user_id in session:
        del session[user_id]
        await event.reply("❌ تم إلغاء العملية.")
    else:
        await event.reply("⚠️ لا توجد عملية جارية لإلغائها.")

@ABH.on(events.NewMessage)
async def add_reply(event):
    user_id = event.sender_id
    text = event.raw_text
    if text in banned:
        return

    if user_id in session:
        chat_id = session[user_id]['chat_id']
        step = session[user_id]['step']
        reply_type = session[user_id]['type']
        key = get_key(chat_id)

        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('📎 أرسل الآن محتوى الرد (نص أو وسائط)')
        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']

            if reply_type == 'mention':
                content = await mention(event)
                r.hset(key, reply_name, f"text|exact|{content}")
            elif event.message.media:
                try:
                    file_id = event.message.file.id
                    match = 'exact' if reply_type == 'normal' else 'contains'
                    r.hset(key, reply_name, f"media|{match}|{file_id}")
                except Exception:
                    await event.reply('⚠️ فشل في قراءة الوسائط.')
                    del session[user_id]
                    return
            else:
                match = 'exact' if reply_type == 'normal' else 'contains'
                r.hset(key, reply_name, f"text|{match}|{text}")

            await event.reply(f'✅ تم حفظ الرد باسم **{reply_name}**')
            del session[user_id]

@ABH.on(events.NewMessage)
async def use_reply(event):
    chat_id = event.chat_id
    text = event.raw_text
    key = get_key(chat_id)
    all_replies = r.hgetall(key)

    for name, val in all_replies.items():
        typ, match_type, content = val.split("|", 2)
        if (match_type == 'exact' and text == name) or (match_type == 'contains' and name in text):
            if typ == 'text':
                await event.reply(content)
            elif typ == 'media':
                await ABH.send_file(event.chat_id, file=content, reply_to=event.id)
            break

@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    chat_id = event.chat_id
    key = get_key(chat_id)
    all_replies = r.hkeys(key)

    if not all_replies:
        await event.reply("⚠️ لا توجد ردود محفوظة في هذه المجموعة.")
    else:
        msg = "\n".join(f"↢ {name}" for name in all_replies)
        await event.reply(f"📋 قائمة الردود:\n{msg}")

@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    chat_id = event.chat_id
    reply_name = event.pattern_match.group(1)
    key = get_key(chat_id)

    if r.hexists(key, reply_name):
        r.hdel(key, reply_name)
        await event.reply(f"🗑️ تم حذف الرد **{reply_name}**")
    else:
        await event.reply("⚠️ هذا الرد غير موجود.")

@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    chat_id = event.chat_id
    key = get_key(chat_id)
    if r.exists(key):
        r.delete(key)
        await event.reply("🗑️ تم حذف جميع الردود من هذه المجموعة.")
    else:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
