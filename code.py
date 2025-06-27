from telethon import events
from ABH import ABH
from Resources import mention
import redis

r = redis.Redis(decode_responses=True)

session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز']

def get_reply_key(user_id):
    return f"replies:{user_id}"

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

@ABH.on(events.NewMessage(pattern='^الغاء$'))
async def cancel_process(event):
    user_id = event.sender_id
    if user_id in session:
        del session[user_id]
        await event.reply("❌ تم إلغاء العملية الجارية.")
    else:
        await event.reply("⚠️ لا توجد عملية جارية لإلغائها.")

@ABH.on(events.NewMessage)
async def add_reply(event):
    user_id = event.sender_id
    text = event.raw_text
    msg = event.message

    if text in banned:
        return

    if user_id in session:
        step = session[user_id]['step']
        reply_type = session[user_id]['type']
        key = get_reply_key(user_id)

        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('📎 أرسل الآن محتوى الرد (نص أو وسائط)')

        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']
            if reply_type == 'mention':
                reply_data = {'type': 'text', 'content': await mention(event), 'match': 'exact'}
            elif msg.media:
                try:
                    reply_data = {
                        'type': 'media',
                        'file_id': msg.file.id,
                        'match': 'exact' if reply_type == 'normal' else 'contains'
                    }
                except Exception:
                    await event.reply("❌ فشل في قراءة الوسائط.")
                    del session[user_id]
                    return
            else:
                reply_data = {
                    'type': 'text',
                    'content': text,
                    'match': 'exact' if reply_type == 'normal' else 'contains'
                }

            r.hset(key, reply_name, str(reply_data))
            await event.reply(f"✅ تم حفظ الرد باسم **{reply_name}**")
            del session[user_id]

@ABH.on(events.NewMessage)
async def use_reply(event):
    user_id = event.sender_id
    text = event.raw_text
    key = get_reply_key(user_id)

    if not r.exists(key):
        return

    for name in r.hkeys(key):
        data = eval(r.hget(key, name))
        if (data['match'] == 'exact' and text == name) or (data['match'] == 'contains' and name in text):
            if data['type'] == 'text':
                await event.reply(data['content'])
            elif data['type'] == 'media':
                await ABH.send_file(event.chat_id, file=data['file_id'], reply_to=event.id)
            break

@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    user_id = event.sender_id
    key = get_reply_key(user_id)

    if not r.exists(key):
        await event.reply("⚠️ لا توجد ردود محفوظة.")
        return

    names = r.hkeys(key)
    msg = "\n".join(f"↢ {name}" for name in names)
    await event.reply(f"📋 ردودك:\n{msg}")

@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    user_id = event.sender_id
    name = event.pattern_match.group(1)
    key = get_reply_key(user_id)

    if r.hdel(key, name):
        await event.reply(f"🗑️ تم حذف الرد **{name}**")
    else:
        await event.reply("⚠️ الرد غير موجود.")

@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_all_replies(event):
    user_id = event.sender_id
    key = get_reply_key(user_id)

    if r.delete(key):
        await event.reply("🗑️ تم حذف جميع الردود.")
    else:
        await event.reply("⚠️ لا توجد ردود لحذفها.")
