from Resources import mention
from telethon import events
from ABH import ABH
replys = {}
session = {}
@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    x = event.sender_id
    await event.reply('ارسل الآن **اسم الرد**')
    session[x] = {'step': 'waiting_for_me_reply_name'}
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    x = event.sender_id
    await event.reply('ارسل الآن **اسم الرد**')
    session[x] = {'step': 'waiting_for_reply_name'}
banned = ['وضع ردي', 'وضع رد']
@ABH.on(events.NewMessage)
async def add_reply(event):
    x = event.sender_id
    msg = event.message
    if msg.text in banned:
        return
    if x in session:
        user_step = session[x].get('step')
        if user_step == 'waiting_for_reply_name':
            session[x]['reply_name'] = event.raw_text
            session[x]['step'] = 'waiting_for_reply_content'
            await event.reply('أرسل الآن **محتوى الرد** سواءً نصًا أو وسائط')
        elif user_step == 'waiting_for_reply_content':
            reply_name = session[x]['reply_name']
            if x not in replys:
                replys[x] = {}
            if msg.media:
                file_id = None
                try:
                    file_id = msg.file.id
                except Exception as e:
                    await event.reply('فشل في الحصول على الملف. تأكد من أن الوسائط مدعومة.')
                    del session[x]
                    return
                replys[x][reply_name] = {
                    'type': 'media',
                    'file_id': file_id
                }
                await event.reply(f'تم حفظ الرد الوسائطي باسم **{reply_name}**')
            else:
                replys[x][reply_name] = {
                    'type': 'text',
                    'content': event.raw_text
                }
                await event.reply(f'تم حفظ الرد النصي باسم **{reply_name}**')
            del session[x]
            return
        elif user_step == 'waiting_for_reply_name':
            session[x]['reply_name'] = event.raw_text
            replys[x][reply_name] = {
                'type': 'text',
                'content': await mention(event)
            }
            await event.reply('تم اضافه الرد')
@ABH.on(events.NewMessage)
async def use_reply(event):
    x = event.sender_id
    if x in replys:
        user_replies = replys[x]
        text = event.raw_text
        if text in user_replies:
            reply_data = user_replies[text]
            if reply_data['type'] == 'text':
                await event.reply(reply_data['content'])
            elif reply_data['type'] == 'media':
                await event.respond(file=reply_data['file_id'])
