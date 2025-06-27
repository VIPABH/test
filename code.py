import json
from Resources import mention
from telethon import events
from ABH import ABH

banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز']
session = {}

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

@ABH.on(events.NewMessage)
async def add_reply(event):
    user_id = event.sender_id
    msg = event.message
    text = msg.text or ""

    if text in banned:
        return

    if user_id in session:
        step = session[user_id]['step']
        reply_type = session[user_id]['type']
        chat_id = session[user_id]['chat_id']
        redis = await get_redis()

        # جلب الردود من ريديس الخاصة بالمجموعة
        stored = await redis.get(f"replys:{chat_id}")
        if stored:
            replys = json.loads(stored)
        else:
            replys = {}

        # إذا المجموعة لا تملك ردود بعد
        if chat_id not in replys:
            replys[chat_id] = {}

        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('📎 أرسل الآن محتوى الرد (نص فقط)')
            return

        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']

            # التحقق من وجود الاسم مسبقا
            if reply_name in replys[chat_id]:
                await event.reply(f"⚠️ اسم الرد **{reply_name}** موجود مسبقاً، يرجى اختيار اسم آخر.")
                return

            # بالنسبة للنوع 'mention' أو 'normal' لا نستقبل وسائط (فيديو أو صورة) بل نص فقط
            if reply_type == 'mention':
                content = await mention(event)
                replys[chat_id][reply_name] = {'type': 'text', 'content': content, 'match': 'exact'}

            elif reply_type in ['normal', 'special']:
                # فقط نص، لا تسمح بالوسائط
                if msg.media:
                    await event.reply('⚠️ أمر "وضع رد" لا يقبل الوسائط، يرجى إرسال نص فقط.')
                    del session[user_id]
                    return

                replys[chat_id][reply_name] = {
                    'type': 'text',
                    'content': text,
                    'match': 'startswith' if reply_type == 'special' else 'exact'
                }

            # حفظ الردود في ريديس
            await redis.set(f"replys:{chat_id}", json.dumps(replys, ensure_ascii=False))
            await event.reply(f'✅ تم حفظ الرد باسم **{reply_name}**')
            del session[user_id]

@ABH.on(events.NewMessage)
async def use_reply(event):
    chat_id = event.chat_id
    text = event.raw_text or ""
    redis = await get_redis()
    stored = await redis.get(f"replys:{chat_id}")

    if not stored:
        return

    replys = json.loads(stored)
    if chat_id not in replys:
        return

    for name, data in replys[chat_id].items():
        if (data['match'] == 'exact' and text == name) or \
           (data['match'] == 'startswith' and text.startswith(name)) or \
           (data['match'] == 'contains' and name in text):
            if data['type'] == 'text':
                await event.reply(data['content'])
            elif data['type'] == 'media':
                await ABH.send_file(chat_id, file=data['file_id'], reply_to=event.id)
            break

@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    chat_id = event.chat_id
    redis = await get_redis()
    stored = await redis.get(f"replys:{chat_id}")

    if not stored:
        await event.reply("⚠️ لا توجد أي ردود محفوظة.")
        return

    replys = json.loads(stored)
    if chat_id not in replys or not replys[chat_id]:
        await event.reply("⚠️ لا توجد أي ردود محفوظة.")
        return

    msg = "\n".join(f" {k}" for k in replys[chat_id])
    await event.reply(f"📋 ردود المجموعة:\n{msg}")

@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    chat_id = event.chat_id
    reply_name = event.pattern_match.group(1)
    redis = await get_redis()
    stored = await redis.get(f"replys:{chat_id}")

    if not stored:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
        return

    replys = json.loads(stored)
    if chat_id in replys and reply_name in replys[chat_id]:
        del replys[chat_id][reply_name]
        await redis.set(f"replys:{chat_id}", json.dumps(replys, ensure_ascii=False))
        await event.reply(f"🗑️ تم حذف الرد **{reply_name}**")
    else:
        await event.reply("⚠️ الرد غير موجود.")

@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    chat_id = event.chat_id
    redis = await get_redis()
    stored = await redis.get(f"replys:{chat_id}")

    if not stored:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
        return

    replys = json.loads(stored)
    if chat_id in replys:
        replys[chat_id] = {}
        await redis.set(f"replys:{chat_id}", json.dumps(replys, ensure_ascii=False))
        await event.reply("🗑️ تم حذف جميع الردود.")
    else:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
