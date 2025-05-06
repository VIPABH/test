from telethon import TelegramClient, events, Button
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH'))
bot_token = os.getenv('BOT_TOKEN')
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change(event):
    await event.message.reply(
        "ارسل اللقب",
        buttons=Button.force_reply(selective=True)
    )

@bot.on(events.NewMessage(pattern="^.رفع مشرف$"))
async def change(event):
    button = [
        Button.inline("👎تغيير معلومات", data="change"),
        Button.inline("👎حذف", data="delete"),
        Button.inline("👎حظر", data="ban"),
        Button.inline("👎دعوة", data="invite"),
        Button.inline("👎ادارة القصص", data="story"),
        Button.inline("👎ادارة المحادثات", data="video_call"),
        Button.inline("👎اضافة مشرفين", data="add_admin"),
    ]
    await event.message.reply(
        "حدد الصلاحيات وارسل اللقب",
        buttons=button,
        reply_markup=Button.force_reply(selective=True)
    )

# Callback queries handling
@bot.on(events.CallbackQuery(func=lambda call: call.data == b"change"))
async def change(event):
    global change
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    delete = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"delete"))
async def change(event):
    global delete
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    change = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"ban"))
async def change(event):
    global ban
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    ban = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"invite"))
async def change(event):
    global invite
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    invite = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"story"))
async def change(event):
    global story
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    story = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"video_call"))
async def change(event):
    global video_call
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    video_call = True

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"add_admin"))
async def change(event):
    global add_admin
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return
    add_admin = True

bot.run_until_disconnected()
