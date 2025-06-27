from Resources import mention
from telethon import events
from ABH import ABH
replys = {}
session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز']
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'normal'}
@ABH.on(events.NewMessage(pattern='^وضع رد مميز$'))
async def set_special_reply(event):
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'special'}
@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    user_id = event.sender_id
    await event.reply('📝 أرسل اسم الرد الآن')
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'mention'}

@ABH.on(events.NewMessage)
async def add_reply(event):
    user_id = event.sender_id
    msg = event.message
    text = msg.text or ""
    
    # لا تستجيب إذا الرسالة من أوامر ممنوعة
    if text in banned:
        return
    
    if user_id in session:
        step = session[user_id]['step']
        reply_type = session[user_id]['type']
        chat_id = session[user_id]['chat_id']
        redis = await get_redis()
        
        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('📎 أرسل الآن محتوى الرد (نص أو وسائط)')
        
        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']
            
            # جلب الردود المخزنة للمجموعة
            stored = await redis.get(f"replys:{chat_id}")
            if stored:
                replys = json.loads(stored)
            else:
                replys = {}

            # تهيئة مكان التخزين
            if reply_name in replys:
                await event.reply(f"⚠️ اسم الرد **{reply_name}** موجود مسبقاً، يرجى اختيار اسم آخر.")
                return

            # بناء الرد
            if reply_type == 'mention':
                content = await mention(event)
                replys[reply_name] = {'type': 'text', 'content': content, 'match': 'exact'}
            elif msg.media:
                try:
                    replys[reply_name] = {
                        'type': 'media',
                        'file_id': msg.file.id,
                        'match': 'startswith' if reply_type == 'special' else 'exact'
                    }
                except Exception:
                    await event.reply('⚠️ فشل في قراءة الوسائط.')
                    del session[user_id]
                    return
            else:
                replys[reply_name] = {
                    'type': 'text',
                    'content': text,
                    'match': 'startswith' if reply_type == 'special' else 'exact'
                }
            
            # حفظ في ريديس
            await redis.set(f"replys:{chat_id}", json.dumps(replys, ensure_ascii=False))
            await event.reply(f'✅ تم حفظ الرد باسم **{reply_name}**')
            del session[user_id]
@ABH.on(events.NewMessage)
async def use_reply(event):
    user_id = event.sender_id
    text = event.raw_text
    if user_id not in replys:
        return
    for name, data in replys[user_id].items():
        if (data['match'] == 'exact' and text == name) or (data['match'] == 'contains' and name in text):
            if data['type'] == 'text':
                await event.reply(data['content'])
            elif data['type'] == 'media':
                await ABH.send_file(event.chat_id, file=data['file_id'], reply_to=event.id)
            break
@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    user_id = event.sender_id
    if user_id not in replys or not replys[user_id]:
        await event.reply(" لا توجد أي ردود محفوظة.")
        return
    msg = "\n".join(f" {k}" for k in replys[user_id])
    await event.reply(f"📋 ردودك:\n{msg}")
@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    user_id = event.sender_id
    reply_name = event.pattern_match.group(1)
    if user_id in replys and reply_name in replys[user_id]:
        del replys[user_id][reply_name]
        await event.reply(f"🗑️ تم حذف الرد **{reply_name}**")
    else:
        await event.reply("⚠️ الرد غير موجود.")
@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    user_id = event.sender_id
    if user_id in replys:
        del replys[user_id]
        await event.reply("🗑️ تم حذف جميع الردود.")
    else:
        await event.reply(" لا توجد ردود لحذفها.")
