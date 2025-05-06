from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import os

# إعدادات البوت
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# معرف المستخدم المصرح له
authorized_user_id = 1910015590

# معرف القناة أو المجموعة التي سيتم رفع المشرف فيها
chat_id = 'اسم_المجموعة_أو_رقم_المجموعة'

# دالة لرفع المستخدم إلى مشرف
async def promote_user(event):
    if event.sender_id == authorized_user_id:
        try:
            # رفع المستخدم مشرفًا في المجموعة
            await bot(EditAdminRequest(
                chat_id=chat_id,
                user_id=event.reply_to_msg_id.sender_id,  # المستخدم الذي سيتم رفعه
                is_admin=True,
                rights=ChatAdminRights(add_admins=True, invite_to_channel=True, change_info=True, ban_users=True)
            ))
            await event.reply("تم رفع المستخدم مشرفًا بنجاح!")
        except Exception as e:
            await event.reply(f"حدث خطأ أثناء رفع المستخدم: {e}")

# Handler للرسائل
@bot.on(events.NewMessage(pattern="^رفع مشرف$"))
async def assign_permissions(event):
    # التحقق إذا كان المرسل هو المصرح له
    if event.sender_id == authorized_user_id:
        if event.is_reply:  # إذا كان المرسل يرد على رسالة، سيتم رفع المستخدم الذي رد عليه
            await promote_user(event)
        else:
            await event.reply("يرجى الرد على المستخدم الذي تريد رفعه كـ مشرف.")
    else:
        await event.reply("أنت غير مخول لرفع مشرفين.")

# تشغيل البوت
bot.run_until_disconnected()
