from telethon import TelegramClient, events, Button
import os

# إعدادات البوت
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تعريف المتغيرات العامة
permissions = {
    'change': False,
    'delete': False,
    'ban': False,
    'invite': False,
    'story': False,
    'video_call': False,
    'add_admin': False
}

# معرف المستخدم المصرح له
authorized_user_id = 1910015590

# دالة لتحديث صلاحيات المستخدم بناءً على اختياراته
async def update_permission(permission, event):
    """تحديث صلاحيات المستخدم بناءً على الإجراء الذي تم اختياره."""
    global permissions
    if event.sender_id == authorized_user_id:
        permissions[permission] = True
        await event.answer(f"تم تفعيل صلاحية {permission}")

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
        Button.inline("👎تغيير معلومات", data="change"),
        Button.inline("👎حذف", data="delete"),
        Button.inline("👎حظر", data="ban"),
        Button.inline("👎دعوة", data="invite"),
        Button.inline("👎ادارة القصص", data="story"),
        Button.inline("👎ادارة المحادثات", data="video_call"),
        Button.inline("👎اضافة مشرفين", data="add_admin"),
        Button.inline("✔️رفع الصلاحيات", data="finalize")  # زر رفع الصلاحيات
    ]
    # استخدم send_message بدلاً من reply
    await event.client.send_message(
        event.chat_id, 
        "حدد الصلاحيات وارسل اللقب", 
        buttons=button
    )

# Callback handlers for different actions
@bot.on(events.CallbackQuery(func=lambda call: call.data == b"change"))
async def change_info(event):
    await update_permission('change', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"delete"))
async def delete_info(event):
    await update_permission('delete', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"ban"))
async def ban_user(event):
    await update_permission('ban', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"invite"))
async def invite_user(event):
    await update_permission('invite', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"story"))
async def manage_story(event):
    await update_permission('story', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"video_call"))
async def manage_video_call(event):
    await update_permission('video_call', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"add_admin"))
async def add_admin_permissions(event):
    await update_permission('add_admin', event)

@bot.on(events.CallbackQuery(func=lambda call: call.data == b"finalize"))
async def finalize_permissions(event):
    if event.sender_id == authorized_user_id:
        # رفع الصلاحيات: تعيين المستخدم مشرفًا في المجموعة
        try:
            # الحصول على صلاحيات المستخدم في المجموعة
            permissions = {
                "change": True,  # مثال على تفعيل صلاحيات
                "delete": True,
                "ban": True,
                "invite": True,
                "story": True,
                "video_call": True,
                "add_admin": True
            }

            # تحديث صلاحيات المستخدم
            await event.client.edit_permissions(
                event.chat_id, 
                event.sender_id, 
                is_admin=True,  # تحديد الصلاحية كمشرف
                change_info=permissions['change'],  # تحديد صلاحيات محددة
                ban_users=permissions['ban'],
                invite_to_group=permissions['invite'],
                manage_call=permissions['video_call'],
                manage_stories=permissions['story'],
                add_admins=permissions['add_admin']
            )

            await event.answer("تم رفع الصلاحيات بنجاح!")
        except Exception as e:
            await event.answer(f"حدث خطأ: {str(e)}")
    else:
        await event.answer("أنت غير مصرح لك بإجراء هذا الأمر.")
bot.run_until_disconnected()
