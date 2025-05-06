from telethon import TelegramClient, events, Button
import os

# إعدادات البوت
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# معرف المستخدم المصرح له
authorized_user_id = 1910015590

# صلاحيات المستخدم (قيد الاستخدام)
permissions = {
    'change': False,
    'delete': False,
    'ban': False,
    'invite': False,
    'story': False,
    'video_call': False,
    'add_admin': False
}

# دالة مشتركة لتحديث الصلاحيات
async def set_permission(permission, event):
    if event.sender_id == authorized_user_id:
        permissions[permission] = True
        await event.answer(f"تم تفعيل صلاحية: {permission}")

# Handler for "تغيير لقبي"
@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change_nickname(event):
    await event.reply("ارسل اللقب", buttons=Button.force_reply(selective=True))

# Handler for "رفع مشرف"
@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    buttons = [
        Button.inline("👎تغيير معلومات", data="change"),
        Button.inline("👎حذف", data="delete"),
        Button.inline("👎حظر", data="ban"),
        Button.inline("👎دعوة", data="invite"),
        Button.inline("👎ادارة القصص", data="story"),
        Button.inline("👎ادارة المحادثات", data="video_call"),
        Button.inline("👎اضافة مشرفين", data="add_admin"),
    ]
    await event.client.send_message(
        event.chat_id,
        "حدد الصلاحيات التي تريد تفعيلها:",
        buttons=buttons
    )

# Callback handler for all buttons
@bot.on(events.CallbackQuery(func=lambda call: call.data in permissions.keys()))
async def handle_callback(event):
    permission = event.data.decode("utf-8")  # استخراج البيانات من الزر
    await set_permission(permission, event)

# تشغيل البوت
bot.run_until_disconnected()
