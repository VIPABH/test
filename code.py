from Resources import mention
from telethon import events
from ABH import ABH
import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز', 'الغاء', 'حذف رد', 'حذف الردود', 'عرض الردود']
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    user_id = event.sender_id
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'normal', 'chat_id': event.chat_id}
    await event.reply('📝 أرسل اسم الرد الآن')
@ABH.on(events.NewMessage(pattern='^وضع رد مميز$'))
async def set_special_reply(event):
    user_id = event.sender_id
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'special', 'chat_id': event.chat_id}
    await event.reply('📝 أرسل اسم الرد الآن')
@ABH.on(events.NewMessage(pattern=r'^وضع ردي (.+)$'))
async def set_my_reply(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    reply_name = event.pattern_match.group(1).strip()
    if not reply_name:
        await event.reply('عذراً، يجب كتابة اسم الرد مع الأمر.')
        return
    redis_key = f"replys:{chat_id}:{reply_name}"
    user_reply_key = f"user_reply:{chat_id}:{user_id}"
    if r.exists(user_reply_key):
        await event.reply("⚠️ لديك رد مسجل بالفعل، الرجاء حذف ردك الحالي قبل إنشاء رد جديد.")
        return
    if r.exists(redis_key):
        await event.reply(f"⚠️ الرد **{reply_name}** موجود مسبقاً، يرجى اختيار اسم آخر.")
        return
    try:
        content = await mention(event)
        r.hset(redis_key, mapping={
            'type': 'text',
            'content': content,
            'match': 'exact'
        })
        r.set(user_reply_key, reply_name)
        await event.reply(f"👍🏾 تم حفظ الرد باسم **{reply_name}**")
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء إعداد الرد: {e}")
@ABH.on(events.NewMessage(pattern='^حذف ردي$'))
async def delete_my_reply(event):
    chat_id = event.chat_id
    user_id = event.sender_id
    user_reply_key = f"user_reply:{chat_id}:{user_id}"
    if not r.exists(user_reply_key):
        await event.reply("⚠️ لا يوجد رد مسجل باسمك لحذفه.")
        return
    reply_name = r.get(user_reply_key)
    redis_key = f"replys:{chat_id}:{reply_name}"
    r.delete(redis_key)
    r.delete(user_reply_key)
    await event.reply(f"🗑️ تم حذف ردك **{reply_name}** بنجاح.")
@ABH.on(events.NewMessage)
async def handle_reply(event):
    user_id = event.sender_id
    msg = event.message
    text = msg.text or ""
    if text in banned:
        return
    if user_id in session:
        current = session[user_id]
        step = current['step']
        reply_type = current['type']
        chat_id = current['chat_id']
        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('📎 أرسل الآن محتوى الرد (نص، وسائط أو منشن)')
            return
        elif step == 'waiting_for_reply_content':
            reply_name = current.get('reply_name')
            redis_key = f"replys:{chat_id}:{reply_name}"
            if r.exists(redis_key):
                await event.reply(f" الرد **{reply_name}** موجود مسبقاً. يرجى اختيار اسم آخر.")
                del session[user_id]
                return
            if reply_type == 'mention':
                content = await mention(event)
                r.hset(redis_key, mapping={
                    'type': 'text',
                    'content': content,
                    'match': 'exact'
                })
            elif msg.media:
                file_id = getattr(msg.file, "id", None)
                if not file_id:
                    await event.reply(" لا يمكن قراءة الوسائط.")
                    del session[user_id]
                    return
                r.hset(redis_key, mapping={
                    'type': 'media',
                    'file_id': file_id,
                    'match': 'startswith' if reply_type == 'special' else 'exact'
                })
            else:
                r.hset(redis_key, mapping={
                    'type': 'text',
                    'content': text,
                    'match': 'startswith' if reply_type == 'special' else 'exact'
                })
            await event.reply(f" تم حفظ الرد باسم **{reply_name}**")
            del session[user_id]
            return
    await execute_reply(event)
async def execute_reply(event):
    chat_id = event.chat_id
    text = event.raw_text or ""
    pattern = f"replys:{chat_id}:*"
    for key in r.scan_iter(match=pattern):
        reply_name = key.split(":", 2)[-1]
        data = r.hgetall(key)
        match_type = data.get('match')
        if (match_type == 'exact' and text == reply_name) or \
           (match_type == 'startswith' and text.startswith(reply_name)) or \
           (match_type == 'contains' and reply_name in text):
            if data.get('type') == 'text':
                await event.reply(data.get('content', ''))
            elif data.get('type') == 'media':
                await ABH.send_file(event.chat_id, file=data.get('file_id'), reply_to=event.id)
            break
@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    chat_id = event.chat_id
    pattern = f"replys:{chat_id}:*"
    keys = list(r.scan_iter(match=pattern))
    if not keys:
        await event.reply(" لا توجد ردود محفوظة.")
        return
    msg = "\n".join(f"⊕ {key.split(':', 2)[-1]}" for key in keys)
    await event.reply(f"📋 قائمة الردود:\n{msg}")
@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    chat_id = event.chat_id
    reply_name = event.pattern_match.group(1).strip()
    if not reply_name:
        await event.reply('عذرا لازم تكتب اسم الرد وي الامر')
        return
    key = f"replys:{chat_id}:{reply_name}"
    if r.exists(key):
        r.delete(key)
        await event.reply(f"🗑️ تم حذف الرد **{reply_name}**")
    else:
        await event.reply(" الرد غير موجود.")
@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    chat_id = event.chat_id
    pattern = f"replys:{chat_id}:*"
    keys = list(r.scan_iter(match=pattern))
    if keys:
        r.delete(*keys)
        await event.reply("🗑️ تم حذف جميع الردود.")
    else:
        await event.reply(" لا توجد ردود لحذفها.")
@ABH.on(events.NewMessage(pattern='^الغاء$'))
async def cancel(event):
    id = event.sender_id
    if id in session:
        del session[id]
        await event.reply('تم الغاء اضافه رد')
    else:
        return
