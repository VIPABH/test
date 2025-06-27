from Resources import mention
from telethon import events
from ABH import ABH
replys = {}
session = {}
banned = ['وضع ردي', 'وضع رد']
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    user_id = event.sender_id
    await event.reply('يتم وضع رد \n ارسل اسم الرد')
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'normal'}
@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    user_id = event.sender_id
    await event.reply('يتم وضع رد \n ارسل اسم الرد')
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'special'}
@ABH.on(events.NewMessage)
async def add_reply(event):
    user_id = event.sender_id
    msg = event.message
    text = msg.text
    if text in banned:
        return
    if user_id in session:
        step = session[user_id]['step']
        reply_type = session[user_id]['type']
        if step == 'waiting_for_reply_name':
            session[user_id]['reply_name'] = text
            session[user_id]['step'] = 'waiting_for_reply_content'
            await event.reply('أرسل الآن **محتوى الرد** سواءً كان نصًا أو وسائط')
        elif step == 'waiting_for_reply_content':
            reply_name = session[user_id]['reply_name']
            if user_id not in replys:
                replys[user_id] = {}
            if reply_type == 'special':
                replys[user_id][reply_name] = {
                    'type': 'text',
                    'content': await mention(event)
                }
                await event.reply(f'🤙🏾 تم حفظ الرد باسم **{reply_name}**')
            elif msg.media:
                try:
                    file_id = msg.file.id
                    replys[user_id][reply_name] = {
                        'type': 'media',
                        'file_id': file_id
                    }
                    await event.reply(f'🤙🏾 تم حفظ الرد باسم **{reply_name}**')
                except Exception:
                    await event.reply(' فشل في الحصول على الملف. تأكد من أن الوسائط مدعومة.')
            else:
                replys[user_id][reply_name] = {
                    'type': 'text',
                    'content': text
                }
                await event.reply(f'🤙🏾 تم حفظ الرد باسم **{reply_name}**')
            del session[user_id]
@ABH.on(events.NewMessage)
async def use_reply(event):
    user_id = event.sender_id
    text = event.raw_text
    if user_id in replys:
        user_replies = replys[user_id]
        if text in user_replies:
            reply_data = user_replies[text]
            if reply_data['type'] == 'text':
                await event.reply(reply_data['content'])
            elif reply_data['type'] == 'media':
                await event.respond(file=reply_data['file_id'])
