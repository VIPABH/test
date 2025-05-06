from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تخزين الجلسات المؤقتة لكل مستخدم يطلب رفع مشرف
admin_sessions = {}

@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    sender = event.sender_id

    if not event.is_reply:
        await event.reply("يرجى الرد على رسالة المستخدم الذي تريد رفعه.")
        return

    reply = await event.get_reply_message()
    target_user = reply.sender_id

    # تهيئة الجلسة
    admin_sessions[sender] = {
        "target_id": target_user,
        "rights": ChatAdminRights()
    }

    await event.reply(
        "اختر الصلاحيات التي تريد منحها ثم اضغط على تنفيذ:",
        buttons=[
            [Button.inline("تعديل المعلومات", b"edit")],
            [Button.inline("حظر المستخدمين", b"ban")],
            [Button.inline("حذف الرسائل", b"delete")],
            [Button.inline("تثبيت الرسائل", b"pin")],
            [Button.inline("دعوة مستخدمين", b"invite")],
            [Button.inline("إدارة الدعوات", b"invite_link")],
            [Button.inline("إدارة الرسائل", b"messages")],
            [Button.inline("✅ تنفيذ الرفع", b"promote")],
            [Button.inline("❌ إلغاء", b"cancel")],
        ]
    )

# تحديث صلاحيات مؤقتة في الجلسة
def update_rights(user_id, **kwargs):
    if user_id in admin_sessions:
        rights = admin_sessions[user_id]['rights']
        for k, v in kwargs.items():
            setattr(rights, k, v)

# تعامل مع ضغط الأزرار
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = event.sender_id
    chat = event.chat_id
    data = event.data.decode()

    if sender not in admin_sessions:
        await event.answer("يرجى بدء العملية من خلال أمر 'رفع مشرف'.")
        return

    if data == "cancel":
        admin_sessions.pop(sender, None)
        await event.edit("❌ تم إلغاء العملية.")
        return

    if data == "promote":
        session = admin_sessions.pop(sender)
        try:
            await bot(EditAdminRequest(
                channel=chat,
                user_id=session['target_id'],
                admin_rights=session['rights'],
                rank="مشرف"
            ))
            await event.edit("✅ تم رفع المستخدم مشرفًا بنجاح.")
        except Exception as e:
            await event.edit(f"حدث خطأ: {e}")
        return

    # تحديث الحقوق حسب الزر
    permission_map = {
        "edit": {"change_info": True},
        "ban": {"ban_users": True},
        "delete": {"delete_messages": True},
        "pin": {"pin_messages": True},
        "invite": {"invite_users": True},
        "invite_link": {"manage_invite_links": True},
        "messages": {"manage_chat": True},
    }

    if data in permission_map:
        update_rights(sender, **permission_map[data])
        await event.answer("✅ تمت إضافة الصلاحية.")

@bot.on(events.NewMessage(pattern="^تغيير لقبي$"))
async def change_nickname(event):
    if not event.is_reply:
        await event.reply("يرجى الرد على رسالة تحتوي على اللقب الجديد.")
        return

    reply = await event.get_reply_message()
    new_rank = reply.text
    chat = event.chat_id

    try:
        await bot(EditAdminRequest(
            channel=chat,
            user_id=event.sender_id,
            admin_rights=ChatAdminRights(),  # لا تغيّر الصلاحيات
            rank=new_rank
        ))
        await event.reply("✅ تم تغيير اللقب بنجاح.")
    except Exception as e:
        await event.reply(f"حدث خطأ: {e}")

bot.run_until_disconnected()
