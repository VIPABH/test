from ABH import *
from telethon import Button
@ABH.on(events.NewMessage(pattern="^/start$"))
async def start(e):
    if e.is_private:
        id = e.sender_id
        if id == 1910015590:
            admin_buttons = [
                [
                    Button.inline("اوامر النشر", data='posting_commands'),
                    Button.inline("اوامر المحظورين", data='banned_commands')
                ],
                [
                    Button.inline("اوامر الاشتراك الاجباري", data='subscribe_commands')
                ]
            ]
            return await e.reply(
                '**أهلاً زعيم، شنو تحب تسوي؟ 👇🏾**', 
                buttons=admin_buttons
            )            
        user_buttons = [
            Button.url("➕ أضفني لمجموعتك", url=f"https://t.me/vipabh_bot?startgroup=true&admin=ban_users+delete_messages+restrict_members+invite_users+pin_messages+change_info"),
            Button.url("📢 القناة", url=f"https://t.me/{CHANNEL_KEY}")
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
@ABH.on(events.CallbackQuery(pattern=r'(posting_commands|banned_commands|subscribe_commands)'))
async def callback_handler(event):
    data = event.data.decode()    
    if data == 'posting_commands':
        buttons = [
            [
                Button.inline("انشاء رسالة", data='creat_message'),
                Button.inline("التقاط رسالة", data='catch_message')
            ]
        ]
    elif data == 'banned_commands':
        buttons = [
            [
                Button.inline("حظر عضو", data='ban_user'),
                Button.inline("الغاء حظر عضو", data='unban_user')
            ],
            [
                Button.inline("المحظورين", data='banned_users')
            ]
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
            ]
        ]        
    await event.edit(f'اختر احد الازرار من قائمة {callbacknames[data]}', buttons=buttons)
