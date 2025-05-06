from telethon import TelegramClient, events, Button
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تعريف المتغيرات العامة
change = False
delete = False
ban = False
invite = False
story = False
video_call = False
add_admin = False

# Handler for "تغيير لقبي"
@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change_nickname(event):
    await event.reply(
        "ارسل اللقب",
        buttons=Button.force_reply(selective=True)
    )

# Handler for "رفع مشرف"
@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    button = [
        Button.inline("👎تغيير معلومات", data="change"),        Button.inline("👎حذف", data="delete"),
        Button.inline("👎حظر", data="ban"),        Button.inline("👎دعوة", data="invite"),
        Button.inline("👎ادارة القصص", data="story"),        Button.inline("👎ادارة المحادثات", data="video_call"),
        Button.inline("👎اضافة مشرفين", data="add_admin"),
    ]
    # استخدم send_message بدلاً من reply
    await event.client.send_message(
        event.chat_id,  # نفس الـ chat_id المستخدم في الحدث
        "حدد الصلاحيات وارسل اللقب",  # النص الذي سيظهر في الرسالة
        buttons=button,  # الأزرار المدمجة
        # reply_markup=Button.force_reply(selective=True)  # مربع الرد
    )
# Callback handlers for different actions
@bot.on(events.CallbackQuery(func=lambda call: call.data == b"change"))
async def change_info(event):
    global change
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    change = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"delete"))
async def delete_info(event):
    global delete
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    delete = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"ban"))
async def ban_user(event):
    global ban
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    ban = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"invite"))
async def invite_user(event):
    global invite
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    invite = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"story"))
async def manage_story(event):
    global story
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    story = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"video_call"))
async def manage_video_call(event):
    global video_call
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    video_call = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"add_admin"))
async def add_admin_permissions(event):
    global add_admin
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    add_admin = True

bot.run_until_disconnected()
