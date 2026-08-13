from Resources import *
from ABH import *
settings_items = {
    'addanddel': ['ترقية وصلاحياتها', 'ترقية', 'رفع'],
    'count': ['توب'],
    'games': ['العاب'],
    'group': ["اوامر المقيدة", "اختصارات", "ايدي"],
    'guard': ['بوتات المضافة', 'منع', 'تعديل', 'تحذير'],
    'mem': ['ميم'],
    'other': ['همسة'],
    'reply': ['ردود'],
    'clean': ['تنظيف'],
}
trans = {
    'addanddel': 'الرفع والتنزيل',
    'count': 'الرسائل',
    'games': 'الالعاب',
    'group': 'المجموعة',
    'guard': 'الحماية',
    'mem': 'الميم',
    'other': 'اخرى',
    'reply': 'الردود',
    'clean': 'التنظيف',
    }
settings_button = (Button.inline('اوامر'+trans[item], data=settings_items[item]) for item in settings_items)
@ABH.on(events.NewMessage(pattern='^(عرض الاعدادات|الاعدادات|/settings)$'))
async def settings(e):
    if not e.is_group:return
    a=await auth(e)
    if not a:
        return await chs(e,'عذرا بس ماعندك صلاحية تفتح الاعدادات')
    bot_info=await bot()
    buttons = [
        [Button.inline('🛡️ اوامر الحماية', b'settings:general'),
         Button.inline('👥 اوامر المجموعة', b'settings:group')],
        [Button.inline('🎭 الردود والميمز', b'settings:reply'),
         Button.url("📩 فتح بالخاص", f"https://t.me/{bot_info.username}?start=settings_{e.chat_id}_{e.sender_id}")]]
    await PROFILE_SEND(e,"⚙️ **قائمة الإعدادات:**",buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=b'^settings:(general|group|reply)$'))
async def open_settings_category(e):
    a=await auth(e)
    if not a:
        return await e.answer('🙂')
    category=e.data.decode().split(':')[1]
    buttons=await build_settings_buttons(e.chat_id,category)
    await e.edit(f"⚙️ **{SETTINGS_CATEGORIES[category]['title']}**",buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=b'^settings_back$'))
async def settings_back(e):
    a=await auth(e)
    if not a:return await e.answer('🙂')
    buttons=[
        [Button.inline('🛡️ اوامر الحماية',b'settings:general'),
        Button.inline('👥 اوامر المجموعة',b'settings:group'),],
        [Button.inline('🎭 الردود والميمز',b'settings:reply')]
    ]
    await e.edit("⚙️ **قائمة الإعدادات:**",buttons=buttons)
@ABH.on(events.NewMessage(pattern=r'^/start settings_(-?\d+)_(\d+)$'))
async def private_settings(e):
    if not e.is_private: return
    if e.sender_id != wfffp: return await e.reply('قريبا ...')
    chat_id, user_id = map(int, e.pattern_match.groups())
    a = await auth(e, chat=chat_id, to=user_id)
    if not authers(a, 'المطور الثانوي'): 
        return await e.reply('عذرا بس ماعندك صلاحية تفتح الاعدادات')
    buttons = [
        [Button.inline('ملف الرفع', data=f'config:addanddel:{chat_id}')],
        [Button.inline('🛡️ اوامر الحظر', data=f'config:ban:{chat_id}')]]
    chat = await ABH.get_entity(chat_id)
    photo_file = None
    if chat.photo:
        photo_bytes = await ABH.download_profile_photo(chat, file=bytes)
        if photo_bytes:
            photo_file = BytesIO(photo_bytes)
            photo_file.name = "photo.jpg"
    if photo_file:
        return await e.reply("⚙️ **قائمة الإعدادات:**", file=photo_file, buttons=buttons)
    return await e.reply("⚙️ **قائمة الإعدادات:**", buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=b'^config:(addanddel):'))
async def configcallbck(e):
    msg = await e.get_message()
    chat = e.data.decode().split(':')[-1]
    button = [
        Button.inline('الرتب', data=f'config:addanddel:ranks:{chat}'),
        Button.inline('الاعدادات', data=f'config:addanddel:settings:{chat}'),
        Button.inline('الاوامر كاملة', data=f'config:addanddel:allcommand:{chat}'),
        ]
    await e.edit(f'~~{msg.text}~~\nاختر ما تريد فعله', buttons=button)
@ABH.on(events.CallbackQuery(pattern=b'^config:addanddel:(ranks|settings|allcommand):'))
async def addanddel_callback(e):
    all_data = data = e.data.decode().split(':')
    data = all_data[1]
    if data == 'ranks':
        return await showranks(e, all_data[-1])
    elif data == 'allcommand':
        return await raise_commands(e)
    elif data == 'settings':
        buttons = [
            [Button.inline('صلاحيات الترقية✍🏾', data=f'settings:promote:{data}'),
            Button.inline('اوامر القفل والفتح', data=f'settings:lock:{data}')],
            [Button.inline('تنظيف الرتب', data=f'settings:clean:{data}')]]
        await e.edit("⚙️ **قائمة الإعدادات:**", buttons=buttons)
        return
async def set_buttons(e, chat=None, b=None):
    if not chat:
        chat = e.chat_id
    buttons = [
        [
            Button.inline(
            x,
            data=f'stoggle:{x}:{chat}',
            style='primary' if r.get(f"lock:{chat}:{x}") == "True" else 'danger'
            )
        ]
        for x in ['رفع', 'ترقية', 'الترقية وصلاحياتها']
        ]
    if b:return buttons
    command = e.reply if event_type(e) == 'NewMessage' else e.edit
    await command('اختر من بين الازرار', buttons=buttons)
@ABH.on(events.CallbackQuery(pattern='^stoggle:'))
async def xcallback(event):
    a = await auth(event)
    if not a:
        return await event.answer('🙂')
    _, feature, chat = event.data.decode().split(':')
    required_rank=bannedactions.get(feature)
    if not required_rank:return await event.answer('الخيار غير موجود')
    if not authers(a,required_rank):return await event.answer(f'صلاحيتك ما تأهلك تعدل على {feature}')
    lock_key=f"lock:{chat}:{feature}"
    current=r.get(lock_key)
    new_state="True" if current!="True" else "False"
    r.set(lock_key,new_state)
    status="تفعيل" if new_state=="True" else "تعطيل"
    m=await mention(event)
    await send(
        event,
        f'#القفل_والفتح\n'
        f'{a} ({m})\n'
        f'ايديه (`{event.sender_id}`)\n'
        f'{status} {feature}\n'
    )
    text = "تعطيل" if current and current == "True" else 'تفعيل'
    button = await set_buttons(event, chat=chat, b=True)
    msg = await event.get_message()
    await event.edit(f'~~{msg.text}~~\nتم {status} {feature}', buttons=button)
@ABH.on(events.CallbackQuery(pattern=b'^settings:(promote|lock|clean):'))
async def second_litsener_callback(e):
    _, arg, chat = e.data.decode().split(':')
    if arg == 'promote':return await lock_admin(e)
    elif arg == 'clean':return await clean_ranks(e)
    elif arg == 'lock':return await set_buttons(e, chat=chat)
@ABH.on(events.CallbackQuery(pattern=b'^toggle:(.+?):(.+)$'))
async def toggle_button(event):
    a=await auth(event)
    if not a:
        return await event.answer('🙂')
    category,feature=event.data.decode().split(':',2)[1:]
    required_rank=bannedactions.get(feature)
    if not required_rank:
        return await event.answer('الخيار غير موجود')
    if not authers(a,required_rank):
        return await event.answer(f'صلاحيتك ما تأهلك تعدل على {feature}')
    lock_key=f"lock:{event.chat_id}:{feature}"
    current=r.get(lock_key)
    new_state="True" if current!="True" else "False"
    r.set(lock_key,new_state)
    status="تفعيل" if new_state=="True" else "تعطيل"
    try:
        m=await mention(event)
        await send(
            event,
            f'#القفل_والفتح\n'
            f'{a} ({m})\n'
            f'ايديه (`{event.sender_id}`)\n'
            f'{status} {feature}\n'
            f'الرابط ({await link(event)})'
        )
    except:
        pass
    if category == 'None':
        text = "تعطيل" if current and current == "True" else 'تفعيل'
        button = Button.inline(text, data=f"toggle:{'None'}:{feature}")
        await event.edit(f'تم {status} {feature}', buttons=button)
    else:
        buttons=await build_settings_buttons(event.chat_id,category)
        await event.edit(f'تم {status} {feature}', buttons=buttons)
