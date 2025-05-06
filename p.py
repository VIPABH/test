from telethon import TelegramClient, events, Button
import os

api_id    = int(os.getenv('API_ID'))
api_hash  = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تعريف المتغيرات الخاصة بالصلاحيات
permissions = {
    'change': False,
    'delete': False,
    'ban': False,
    'invite': False,
    'story': False,
    'video_call': False,
    'add_admin': False
}

@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change(event):
    await event.reply(
        "ارسل اللقب",
        buttons=Button.force_reply(selective=True)
    )

@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    button = [
        Button.inline("👎تغيير معلومات", data="change"),
        Button.inline("👎حذف", data="delete"),
        Button.inline("👎حظر", data="ban"),
        Button.inline("👎دعوة", data="invite"),
        Button.inline("👎ادارة القصص", data="story"),
        Button.inline("👎ادارة المحادثات", data="video_call"),
        Button.inline("👎اضافة مشرفين", data="add_admin"),
        Button.inline("✅رفع العضو مشرف", data="promote_admin")  # الزر الجديد لرفع العضو مشرف
    ]
    await event.reply(
        "حدد الصلاحيات وارسل اللقب",
        buttons=button,
        reply_markup=Button.force_reply(selective=True)
    )

@bot.on(events.CallbackQuery(func=lambda call: call.data in [b"change", b"delete", b"ban", b"invite", b"story", b"video_call", b"add_admin", b"promote_admin"]))
async def handle_permissions(event):
    # تعريف المعرّف الخاص بالمسؤول
    wfffp = 1910015590
    uid = event.sender_id
    if not uid == wfffp:
        return

    action = event.data.decode()  # تحويل البايت إلى نص
    if action != "promote_admin":
        permissions[action] = not permissions[action]  # عكس القيمة (إذا كانت True تصبح False والعكس)

    # تعديل الرسالة بناءً على حالة الزر
    new_text = "تم تحديث الصلاحيات:\n"
    for perm, status in permissions.items():
        new_text += f"{perm}: {'👍' if status else '👎'}\n"

    if action == "promote_admin":
        # تحقق من تفعيل صلاحية "إضافة مشرفين" قبل رفع العضو مشرفًا
        if permissions['add_admin']:
            # رفع العضو مشرفًا
            try:
                target_user = event.sender
                await bot.edit_admin(event.chat_id, target_user, is_admin=True)
                new_text += "\nتم رفع العضو مشرفًا بنجاح!"
            except Exception as e:
                new_text += f"\nفشل رفع العضو مشرفًا: {str(e)}"

    # تعديل الرسالة مع الأزرار
    await event.edit(new_text, buttons=event.message.buttons)

# تشغيل البوت
bot.run_until_disconnected()
