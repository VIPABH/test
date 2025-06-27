from Resources import mention
from telethon import events
from ABH import ABH, r
import json, os
x = ["وضع رد", "وضع ردي", "حذف رد", "حذف ردود", "ردود", "/replys"]
user = {}
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    if not event.is_group:
        return
    await event.reply('يتم وضع رد \n اكتب اسم الرد الذي تريد وضعه')
    user[event.sender_id] = 'set_reply'
@ABH.on(events.NewMessage(pattern='^$وضع ردي$'))
async def set_my_reply(event):
    if not event.is_group:
        return
    await event.reply('يتم وضع رد \n اكتب اسم الرد الذي تريد وضعه')
    user[event.sender_id] = 'set_my_reply'
@ABH.on(events.NewMessage(pattern='^حذف رد$'))
async def delete_reply(event):
    if not event.is_group:
        return
    await event.reply('يتم حذف رد \n اكتب اسم الرد الذي تريد حذفه')
    user[event.sender_id] = 'delete_reply'
@ABH.on(events.NewMessage(pattern='^حذف الردود$'))
async def delete_replies(event):
    if not event.is_group:
        return
    await event.reply('تم حذف جميع الردود 🗑️🗑️')
@ABH.on(events.NewMessage(pattern='^ردود$'))
async def get_replies(event):
    if not event.is_group:
        return
    if os.path.exists('replys.json'):
        with open('replys.json', 'r', encoding='utf-8') as f:
            replys = json.load(f)
        replys = [f'**{key}** : {value}' for key, value in replys.items()]
        await event.reply('\n'.join(replys))
    else:
        await event.reply('لا توجد ردود حاليا')
@ABH.on(events.NewMessage)
async def reply_handler(event):
    if not event.is_group:
        return
    if event.sender_id in user:
        action = user[event.sender_id]
        if action == 'set_reply':
            reply_name = event.raw_text
            await event.reply('اكتب الرد الذي تريد وضعه')
            user[event.sender_id] = ('set_reply', reply_name)
        elif action == 'set_my_reply':
            reply_name = event.raw_text
            await event.reply('اكتب الرد الذي تريد وضعه')
            user[event.sender_id] = ('set_my_reply', reply_name)
        elif action == 'delete_reply':
            reply_name = event.raw_text
            if os.path.exists('replys.json'):
                with open('replys.json', 'r', encoding='utf-8') as f:
                    replys = json.load(f)
                if reply_name in replys:
                    del replys[reply_name]
                    with open('replys.json', 'w', encoding='utf-8') as f:
                        json.dump(replys, f, ensure_ascii=False, indent=4)
                    await event.reply(f'تم حذف الرد **{reply_name}**')
                else:
                    await event.reply(f'لا يوجد رد بهذا الاسم: {reply_name}')
            else:
                await event.reply('لا توجد ردود حاليا')
        del user[event.sender_id]
