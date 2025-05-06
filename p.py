from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

# إعدادات البوت
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تعريف المعرف المصرح له
authorized_user_id = 1910015590

# دالة لرفع المستخدم إلى مشرف
async def promote_user(event):
    if event.sender_id == authorized_user_id:
        try:
            # التحقق من أن الرسالة تحتوي على رد
            if event.is_reply:
                replied_message = await event.get_reply_message()
                user_to_promote = replied_message.sender_id  # المستخدم الذي سيتم رفعه
                # استخدام event.chat_id للحصول على معرف المجموعة التي جرى فيها الحدث
                chat_id = event.chat_id
                # رفع المستخدم مشرفًا في المجموعة
                await bot(EditAdminRequest(
                    channel=chat_id,  # استخدام channel بدلاً من chat_id
                    user_id=user_to_promote,
                    is_admin=True,
                    rights=ChatAdminRights(
                        change_info=True,  # السماح بتغيير معلومات المجموعة
                        ban_users=True,    # السماح بحظر المستخدمين
                        delete_messages=True,  # السماح بحذف الرسائل
                        invite_users=True,  # السماح بدعوة المستخدمين
                        pin_messages=True  # السماح بتثبيت الرسائل
                    )
                ))
                await event.reply("تم رفع المستخدم مشرفًا بنجاح!")
            else:
                await event.reply("يرجى الرد على المستخدم الذي تريد رفعه كـ مشرف.")
        except Exception as e:
            await event.reply(f"حدث خطأ أثناء رفع المستخدم: {e}")

# Handler للرسائل
@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    # التحقق إذا كان المرسل هو المصرح له
    if event.sender_id == authorized_user_id:
        await promote_user(event)
    else:
        await event.reply("أنت غير مخول لرفع مشرفين.")

# تشغيل البوت
bot.run_until_disconnected()
