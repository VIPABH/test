from telethon.tl.types import InputDocument
from Resources import mention, hint, wfffp
# from other import botuse, is_assistant
from telethon import Button, events
# from Program import chs
import random, redis
from ABH import ABH
async def chs(e, t):
    ABH.send_message(e.chat_id, t, reply_to=e.id)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
session = {}
banned = ['وضع ردي', 'وضع رد', 'وضع رد مميز', 'الغاء', 'حذف رد', 'حذف الردود', 'عرض الردود', 'حذف ردي']
@ABH.on(events.NewMessage(pattern='^وضع رد$'))
async def set_reply(event):
    if event.sender_id != wfffp:
        await chs(event, 'عذرا الامر فيه صيانه ')
        return
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        await chs(event, 'عذرا بس امر الردود معطل 😑')
        return
    # if not is_assistant(event.chat_id, event.sender_id):
    #     await chs(event, 'عذرا الامر خاص بالمعاونين فقط🤭')
    #     return
    type = "وضع رد"
#    await botuse(type)
    user_id = event.sender_id
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'normal', 'chat_id': event.chat_id}
    await event.reply('📝 أرسل اسم الرد الآن')
@ABH.on(events.NewMessage(pattern='^وضع رد مميز$'))
async def set_special_reply(event):
    if event.sender_id != wfffp:
        await chs(event, 'عذرا الامر فيه صيانه ')
        return
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        await chs(event, 'عذرا بس امر الردود معطل 😑')
        return
    # if not is_assistant(event.chat_id, event.sender_id):
    #     await chs(event, 'عذرا الامر خاص بالمعاونين فقط🤭')
    #     return
    type = "وضع رد مميز"
#    await botuse(type)
    user_id = event.sender_id
    session[user_id] = {'step': 'waiting_for_reply_name', 'type': 'special', 'chat_id': event.chat_id}
    await event.reply('📝 أرسل اسم الرد الآن')
@ABH.on(events.NewMessage(pattern=r'^وضع ردي (.+)$'))
async def set_my_reply(event):
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        await chs(event, 'عذرا بس امر الردود معطل 😑')
        return
    type = "وضع ردي"
#    await botuse(type)
    chat_id = event.chat_id
    user_id = event.sender_id
    reply_name = event.pattern_match.group(1)
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
    type = "حذف ردي"
#    await botuse(type)
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
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        return
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
                if event.media:
                    print('>>')
                    doc = event.message.media.document
                    file_id = InputDocument(
                        id=doc.id,
                        access_hash=doc.access_hash,
                        file_reference=doc.file_reference
                    )
                    if not file_id:
                        await event.reply("لا يمكن قراءة الوسائط.")
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
    chat_id = event.chat_id
    text = event.raw_text or ""
    pattern = f"replys:{chat_id}:*"
    for key in r.scan_iter(match=pattern):
        reply_name = key.split(":", 2)[-1]
        data = r.hgetall(key)
        print(data)
        match_type = data.get('match')
        if (
            (match_type == 'exact' and text == reply_name) or
            (match_type == 'startswith' and text.startswith(reply_name)) or
            (match_type == 'contains' and reply_name in text)
        ):
            if data.get('type') == 'text':
                content = data.get('content')
                if content:
                    await event.reply(content)
                    return
            if data.get('type') == 'media':
                file_id = data.get('file_id')
                if file_id:
                    try:
                        await ABH.send_file(event.chat_id, file=file_id, reply_to=event.id)
                    except Exception as e:
                        await event.reply(f"❌ فشل إرسال الملف: {e}")
                else:
                    await event.reply("⚠️ لا يوجد معرف ملف.")
@ABH.on(events.NewMessage(pattern='^عرض الردود$'))
async def show_replies(event):
    # if not is_assistant(event.chat_id, event.sender_id):
    #     await chs(event, 'عذرا الامر خاص بالمعاونين فقط🤭')
    #     return
    type = "عرض الردود"
#    await botuse(type)
    chat_id = event.chat_id
    pattern = f"replys:{chat_id}:*"
    keys = list(r.scan_iter(match=pattern))
    if not keys:
        await event.reply(" لا توجد ردود محفوظة.")
        return
    msg = "\n".join(f"⊕ ↤ {key.split(':', 2)[-1]}" for key in keys)
    await event.reply(f"📋 قائمة الردود:\n{msg}")
@ABH.on(events.NewMessage(pattern=r"^حذف رد (.+)$"))
async def delete_reply(event):
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        await chs(event, 'عذرا بس امر الردود معطل 😑')
        return
    # if not is_assistant(event.chat_id, event.sender_id):
    #     await chs(event, 'عذرا الامر خاص بالمعاونين فقط🤭')
    #     return
    type = "حذف رد"
#    await botuse(type)
    chat_id = event.chat_id
    reply_name = event.pattern_match.group(1)
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
    lock_key = f"lock:{event.chat_id}:ردود"
    z = r.get(lock_key) == "True"
    if not z:
        await chs(event, 'عذرا بس امر الردود معطل 😑')
        return
    # if not is_assistant(event.chat_id, event.sender_id):
    #     await chs(event, 'عذرا الامر خاص بالمعاونين فقط🤭')
    #     return
    type = "حذف الردود"
#    await botuse(type)
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
    type = "الغاء اضافه رد"
#    await botuse(type)
    id = event.sender_id
    if id in session:
        del session[id]
        await event.reply('تم الغاء اضافه رد')
    else:
        return
abh = [
    "ها",
    "تفظل",
    "كول",
    "اسمعك",
    "شرايد",
    "خلصني"
]
@ABH.on(events.NewMessage(pattern=r'^مخفي$'))
async def anymous(event):
    if event.is_reply or not event.is_group:
        return
    type = "مخفي"
#    await botuse(type)
    vipabh = random.choice(abh)
    await chs(event, vipabh)
@ABH.on(events.NewMessage(pattern=r'^ابن هاشم$'))
async def ABN_HASHEM(event):
    type = "ابن هاشم"
#    await botuse(type)
    caption = "أبن هاشم (رض) مرات متواضع ،🌚 @K_4x1"
    button = [Button.url(text="click", url="https://t.me/wfffp")]
    pic = 'links/vipabh.jpg'
    await event.client.send_file(event.chat_id, pic, caption=caption, reply_to=event.message.id, buttons=button)
auto = [
        "ع س",
        "عليكم السلام",
        "عليكم السلام والرحمة والاكرام",
        "عليكم سلام الله"
        ]
@ABH.on(events.NewMessage(pattern=r'^(سلام عليكم|السلام عليكم)$'))
async def reply_hi(event):
    if not event.is_group:
        return
    type = "السلام عليكم"
#    await botuse(type)
    abh = random.choice(auto)
    await event.reply(abh)
@ABH.on(events.NewMessage(pattern='النازية|الشعار'))
async def nazi(event):
    if not event.is_group:
        return
    type = "النازية"
#    await botuse(type)
    n1 = """🟥🟥🟥🟥🟥🟥🟥🟥🟥
🟥⬜⬜⬜⬜⬜⬜⬜🟥
🟥⬜⬛⬜⬛⬛⬛⬜🟥
🟥⬜️⬛️⬜️⬛️⬜️⬜️⬜️🟥
🟥⬜️⬛️⬛️⬛️⬛️⬛️⬜️🟥
🟥⬜️⬜️⬜️⬛️⬜️⬛️⬜️🟥
🟥⬜️⬛️⬛️⬛️⬜️⬛️⬜️🟥
🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️🟥
🟥🟥🟥🟥🟥🟥🟥🟥🟥
"""
    n2 = """⠙⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢹⠿⣿⣿⣿⣿⣿
⣷⣶⡀⠿⠿⣿⣿⣿⣿⣿⣿⡇⠐⠂⢒⡢⠀⣿⣿⣿
⣿⣿⣿⣆⠀⠈⢻⣿⣿⣿⣿⣿⡆⢈⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣷⣄⠀⠙⠻⢻⢿⣿⠷⢠⢽⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣧⡀⠁⠀⢘⣱⣍⠿⣾⢿⣿⢿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠀⠀⢉⢷⣌⠳⣿⣽⣛⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠋⠽⠶⡌⣿⣻⣀
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣠⡀⠀⠀⠀⠐⠇⢿⣿⣿
⠿⠿⠿⠿⠿⠿⠿⠿⠏⠁⠀⠈⠀⠅⠶⠲⠶⠆⠔⠿"""
    n3 = """⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠟⠛⠉⣩⣍⠉⠛⠻⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⠋⠀⠀⣠⣾⣿⠟⠁⠀⠀⠀⠙⣿⣿⣿⣿
⣿⣿⣿⠁⠀⠀⢾⣿⣟⠁⠀⣠⣾⣷⣄⠀⠘⣿⣿⣿
⣿⣿⡇⣠⣦⡀⠀⠙⢿⣷⣾⡿⠋⠻⣿⣷⣄⢸⣿⣿
⣿⣿⡇⠙⢿⣿⣦⣠⣾⡿⢿⣷⣄⠀⠈⠻⠋⢸⣿⣿
⣿⣿⣿⡀⠀⠙⢿⡿⠋⠀⢀⣽⣿⡷⠀⠀⢠⣿⣿⣿
⣿⣿⣿⣿⣄⠀⠀⠀⢀⣴⣿⡿⠋⠀⠀⣠⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣦⣤⣀⣙⣋⣀⣤⣴⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"""
    abh = random.choice([n1, n2, n3])
    await chs(event, abh)
