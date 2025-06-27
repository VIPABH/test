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
    await event.reply('📥 اكتب اسم الرد الذي تريد وضعه:')
    user[event.sender_id] = 'set_reply'

@ABH.on(events.NewMessage(pattern=r'^وضع ردي$'))
async def set_my_reply(event):
    if not event.is_group:
        return
    await event.reply('📥 اكتب اسم الرد الذي تريد وضعه:')
    user[event.sender_id] = 'set_my_reply'

@ABH.on(events.NewMessage(pattern='^حذف رد$'))
async def delete_reply(event):
    if not event.is_group:
        return
    await event.reply('🗑️ اكتب اسم الرد الذي تريد حذفه:')
    user[event.sender_id] = 'delete_reply'

@ABH.on(events.NewMessage(pattern='^حذف ردود$'))
async def delete_replies(event):
    if not event.is_group:
        return
    if os.path.exists('replys.json'):
        os.remove('replys.json')
        await event.reply('🗑️ تم حذف جميع الردود بنجاح.')
    else:
        await event.reply('🚫 لا توجد ردود لحذفها.')

@ABH.on(events.NewMessage(pattern='^ردود$'))
async def get_replies(event):
    if not event.is_group:
        return
    if os.path.exists('replys.json'):
        with open('replys.json', 'r', encoding='utf-8') as f:
            replys = json.load(f)
        if not replys:
            return await event.reply('📭 لا توجد ردود محفوظة.')
        replys_text = [f'▫️ **{key}** : {value}' for key, value in replys.items()]
        await event.reply('\n'.join(replys_text))
    else:
        await event.reply('📭 لا توجد ردود محفوظة.')

@ABH.on(events.NewMessage)
async def reply_handler(event):
    if not event.is_group or event.raw_text.strip() in x:
        return

    sender_id = event.sender_id
    msg_text = event.raw_text.strip()

    if sender_id in user:
        current = user[sender_id]

        # المرحلة الأولى: استلام اسم الرد
        if current == 'set_reply' or current == 'set_my_reply':
            user[sender_id] = (current, msg_text)
            await event.reply("📩 الآن أرسل محتوى الرد:")
            return

        # المرحلة الثانية: استلام محتوى الرد
        elif isinstance(current, tuple):
            action, reply_name = current
            content = msg_text

            if os.path.exists('replys.json'):
                with open('replys.json', 'r', encoding='utf-8') as f:
                    replys = json.load(f)
            else:
                replys = {}

            replys[reply_name] = content
            with open('replys.json', 'w', encoding='utf-8') as f:
                json.dump(replys, f, ensure_ascii=False, indent=4)

            await event.reply(f'✅ تم حفظ الرد:\n• الاسم: **{reply_name}**\n• المحتوى: {content}')
            del user[sender_id]
            return

        # حذف رد
        elif current == 'delete_reply':
            reply_name = msg_text
            if os.path.exists('replys.json'):
                with open('replys.json', 'r', encoding='utf-8') as f:
                    replys = json.load(f)
                if reply_name in replys:
                    del replys[reply_name]
                    with open('replys.json', 'w', encoding='utf-8') as f:
                        json.dump(replys, f, ensure_ascii=False, indent=4)
                    await event.reply(f'🗑️ تم حذف الرد: **{reply_name}**')
                else:
                    await event.reply(f'🚫 لا يوجد رد بهذا الاسم: **{reply_name}**')
            else:
                await event.reply('🚫 لا توجد ردود محفوظة.')
            del user[sender_id]
            return

    # الرد التلقائي عند التطابق
    if os.path.exists('replys.json'):
        with open('replys.json', 'r', encoding='utf-8') as f:
            replys = json.load(f)
        for name, content in replys.items():
            if msg_text.startswith(name):
                await event.reply(content)
                break
