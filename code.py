from telethon import events
from ABH import ABH

replys = {}     # لتخزين الردود حسب المستخدم
session = {}    # لتتبع حالة المستخدم

# بدء عملية إضافة رد
@ABH.on(events.NewMessage(pattern='^وضع ردي$'))
async def set_my_reply(event):
    x = event.sender_id
    await event.reply('ارسل الآن **اسم الرد**')
    session[x] = {'step': 'waiting_for_reply_name'}
banned = ['وضع ردي']
@ABH.on(events.NewMessage)
async def add_reply(event):
    x = event.sender_id
    if x in banned:
        return
    if x in session:
        user_step = session[x].get('step')

        # الخطوة الأولى: استلام اسم الرد
        if user_step == 'waiting_for_reply_name':
            session[x]['reply_name'] = event.raw_text
            session[x]['step'] = 'waiting_for_reply_content'
            await event.reply('جيد، الآن أرسل **محتوى الرد**')

        # الخطوة الثانية: استلام محتوى الرد
        elif user_step == 'waiting_for_reply_content':
            reply_name = session[x]['reply_name']
            reply_content = event.raw_text

            if x not in replys:
                replys[x] = {}

            replys[x][reply_name] = reply_content
            await event.reply(f'تم حفظ الرد باسم: **{reply_name}**')

            # حذف الجلسة
            del session[x]

# استخدام الردود لاحقًا
@ABH.on(events.NewMessage)
async def use_reply(event):
    x = event.sender_id
    if x in replys:
        user_replies = replys[x]
        text = event.raw_text
        if text in user_replies:
            await event.reply(user_replies[text])
