from ABH import *
from telethon import Button

# دالة مساعدة لعرض قائمة الأدمن الرئيسية لمنع تكرار الكود
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


@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if e.is_private:
        id = e.sender_id
        if id == 1910015590:
            return await send_admin_menu(e, is_callback=False)
            
        user_buttons = [
            [
                Button.url("➕ أضفني لمجموعتك", url=f"https://t.me/vipabh_bot?startgroup=true&admin=ban_users+delete_messages+restrict_members+invite_users+pin_messages+change_info"),
                Button.url("📢 القناة", url=f"https://t.me/{CHANNEL_KEY}")
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

# أضفنا 'back_to_main' للنمط لكي يستجيب البوت لزر العودة
@ABH.on(events.CallbackQuery(pattern=r'(posting_commands|banned_commands|subscribe_commands|back_to_main)'))
async def callback_handler(event):
    data = event.data.decode()    
    
    # إذا ضغط المستخدم على زر العودة
    if data == 'back_to_main':
        return await send_admin_menu(event, is_callback=True)
        
    if data == 'posting_commands':
        buttons = [
            [
                Button.inline("انشاء رسالة", data='creat_message'),
                Button.inline("التقاط رسالة", data='catch_message')
            ],
            [Button.inline("🔙 عودة", data='back_to_main')] # زر العودة
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
            [Button.inline("🔙 عودة", data='back_to_main')] # زر العودة
        ]
    elif data == 'subscribe_commands':
        userslen = r.scard('users')
        buttons = [
            [
                Button.inline(f"المستخدمين ( {userslen} )", data='ban_user'),
                Button.inline("جلب اسامي المستخدمين", data='banned_users')
            ],
            [
                Button.inline("البحث عن مستخدم", data='unban_user')
            ],
            [Button.inline("🔙 عودة", data='back_to_main')] # زر العودة
        ]        
    await event.edit(f'اختر احد الازرار من قائمة {callbacknames[data]}', buttons=buttons)
