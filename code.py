from ABH import *
from telethon import Button
from Resources import *
async def send_admin_menu(event_or_message, is_callback=False):
    admin_buttons = [
        [
            Button.inline("اوامر النشر", data='posting_commands'),
            Button.inline("اوامر المحظورين", data='banned_commands')
        ],
        [
            Button.inline("اوامر الاشتراك الاجباري", data='subscribe_commands')
        ]
    ]
    text = '**أهلاً زعيم، شنو تحب تسوي؟ 👇🏾**'
    
    if is_callback:
        await event_or_message.edit(text, buttons=admin_buttons)
    else:
        await event_or_message.reply(text, buttons=admin_buttons)
REDIS_KEY = "users"
@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    id = e.sender_id
    if id == 8655399180:
        return await send_admin_menu(e, is_callback=False)   
    user_buttons = [
        [
            Button.url("➕ أضفني لمجموعتك", url=f"https://t.me/vipabh_bot?startgroup=true&admin=ban_users+delete_messages+restrict_members+invite_users+pin_messages+change_info"),
        ]
    ]
    await e.reply(
        "أهلاً بك! أنا صانع بوتات.", 
        buttons=user_buttons
    )
callbacknames = {
'posting_commands': 'اوامر النشر', 
'banned_commands': "اوامر المحظورين", 
'subscribe_commands': 'اوامر الاشتراك الاجباري'
}
@ABH.on(events.CallbackQuery(pattern=r'(posting_commands|banned_commands|subscribe_commands|back_to_main)'))
async def callback_handler(event):
    data = event.data.decode()    
    
    if data == 'back_to_main':
        return await send_admin_menu(event, is_callback=True)
        
    if data == 'posting_commands':
        buttons = [
            [
                Button.inline("انشاء رسالة", data='creat_message'),
                Button.inline("التقاط رسالة", data='catch_message')
            ],
            [Button.inline("🔙 عودة", data='back_to_main')] 
        ]
    elif data == 'banned_commands':
        buttons = [
            [
                Button.inline("حظر عضو", data='ban_user'),
                Button.inline("الغاء حظر عضو", data='unban_user')
            ],
            [
                Button.inline("المحظورين", data='banned_users')
            ],
            [Button.inline("🔙 عودة", data='back_to_main')]
        ]
    elif data == 'subscribe_commands':
        userslen = r.scard('users')
        buttons = [
            [
                Button.inline(f"المستخدمين ( {userslen} )", data='ban_user'),
                Button.inline("جلب اسامي المستخدمين", data='banned_users')
            ],
            [
                Button.inline("البحث عن مستخدم", data='serch_user')
            ],
            [Button.inline("🔙 عودة", data='back_to_main')] 
        ]        
    await event.edit(f'اختر احد الازرار من قائمة {callbacknames[data]}', buttons=buttons)
session = {}
@ABH.on(events.CallbackQuery(pattern=r'(ban_user|unban_user|serch_user)'))
async def callback_handler(e):
    data = e.data.decode()
    await e.edit(f'ارسل الان يوزر او ايدي الشخص')
    session[e.sender_id] = data
    await asyncio.sleep(120)
    if e.sender_id not in session: return
    ABH.add_event_handler(get_user, events.NewMessage(chats=e.chat_id))
async def get_user(event):
    id = event.sender_id
    if id not in session: return
    data = session[id]
    t = event.message.text
    target = await to(event, t)
    if not target: return await event.reply('ارسل يوزر او ايدي صالح')
    target_id = getattr(target, "sender_id", None) or getattr(target, "id", None)
    if data == 'ban_user':
        r.sadd("gban_users", target_id)
        m = await ment(target_id)
        await event.reply(f'تم حظر {m} بنجاح')
    elif data == 'unban_user':
        r.srem("gban_users", target_id)
        m = await ment(target_id)
        await event.reply(f'تم فك الحظر بنجاح')
    elif data == 'serch_user':
        is_member = r.sismember(REDIS_KEY, str(target_id))
        if not is_member: return await event.reply('هذا الشخص غير موجود')
        photo = await get_profile_photo(target_id)
        caption = f'''
        اسمه : {target.first_name}
        اسمه بالبوت : {await ment(target_id)}
        ايديه `{target_id}`
        ترتيبه `{await get_order(target_id)}`
        '''
        await ABH.send_file(event.chat_id, photo, caption=caption, reply_to=event.message.id)
    session.pop(id)
    ABH.remove_event_handler(get_user, events.NewMessage(chats=e.chat_id))
