from Resources import mention
from telethon import events
from ABH import ABH
import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز']
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
@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    user_id = event.sender_id
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'mention', 'chat_id': event.chat_id}
    await event.reply('📝 أرسل اسم الرد الآن')

# تخزين الردود
@ABH.on(events.NewMessage)
async def handle_reply_saving(event):
    user_id = event.sender_id
    msg = event.message
    text = msg.text or ""

    # لا نتعامل مع أوامر الإعداد داخل هذه الدالة
    if text in banned:
        return

    # معالجة مرحلة إعداد الردود
    if user_id in session:
        step = session[user_id]['step']
        reply_type = session[user_id]['type']

        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            # await event.reply('📎 أرسل الآن محتوى الرد (نص أو وسائط)')
            return

        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']
            redis_key = f"replys:{user_id}:{reply_name}"

            if r.exists(redis_key):
                await event.reply(f"⚠️ اسم الرد **{reply_name}** موجود مسبقاً، يرجى اختيار اسم آخر.")
                return

            if reply_type == 'mention':
                content = await mention(event)
                r.hset(redis_key, mapping={
                    'type': 'text',
                    'content': content,
                    'match': 'exact'
                })

            elif msg.media:
                try:
                    file_id = getattr(msg.file, "id", None)
                    if not file_id:
                        await event.reply("⚠️ لا يمكن قراءة الوسائط.")
                        del session[user_id]
                        return

                    r.hset(redis_key, mapping={
                        'type': 'media',
                        'file_id': file_id,
                        'match': 'startswith' if reply_type == 'special' else 'exact'
                    })

                except Exception as e:
                    await event.reply(f'⚠️ حدث خطأ أثناء قراءة الوسائط: {e}')
                    del session[user_id]
                    return

            else:
                r.hset(redis_key, mapping={
                    'type': 'text',
                    'content': text,
                    'match': 'startswith' if reply_type == 'special' else 'exact'
                })

            await event.reply(f'✅ تم حفظ الرد باسم **{reply_name}**')
            del session[user_id]
            return

    # إذا لم يكن في جلسة إعداد، يتم فحص الردود الجاهزة
    await check_and_respond(event)


# التحقق من الردود الجاهزة والرد حسب المطابقة
async def check_and_respond(event):
    user_id = event.sender_id
    text = event.raw_text or ""

    pattern = f"replys:{user_id}:*"
    for key in r.scan_iter(match=pattern):
        reply_name = key.split(':', 2)[-1]
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


# عرض الردود
@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    user_id = event.sender_id
    pattern = f"replys:{user_id}:*"
    keys = list(r.scan_iter(match=pattern))

    if not keys:
        await event.reply("⚠️ لا توجد أي ردود محفوظة.")
        return

    msg = "\n".join(f"▫️ {key.split(':', 2)[-1]}" for key in keys)
    await event.reply(f"📋 قائمة الردود:\n{msg}")

# حذف رد واحد
@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    user_id = event.sender_id
    reply_name = event.pattern_match.group(1).strip()
    key = f"replys:{user_id}:{reply_name}"

    if r.exists(key):
        r.delete(key)
        await event.reply(f"🗑️ تم حذف الرد **{reply_name}**")
    else:
        await event.reply("⚠️ الرد غير موجود.")

# حذف جميع الردود
@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    user_id = event.sender_id
    pattern = f"replys:{user_id}:*"
    keys = list(r.scan_iter(match=pattern))

    if keys:
        r.delete(*keys)
        await event.reply("🗑️ تم حذف جميع الردود.")
    else:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
