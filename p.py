from telethon import TelegramClient, events, Button
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.errors.rpcerrorlist import PeerIdInvalidError
import os

# الحصول على متغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تهيئة عميل البوت
ABH = TelegramClient('c', api_id, api_hash).start(bot_token=bot_token)

notification_group_id = None
edited_message = None  # متغير لتخزين الرسالة المعدلة

@ABH.on(events.NewMessage(pattern=r'^اضف كروب (\d+)$'))
async def add_group(event):
    global notification_group_id  # الوصول إلى المتغير العام
    match = event.pattern_match  # استخراج الرقم من الأمر
    if match:
        notification_group_id = int(match.group(1))
        await event.reply(f"تم تعيين الكروب بمعرف: {notification_group_id} ككروب التبليغ.")
    else:
        await event.reply("يرجى إدخال معرف كروب صحيح. مثال: `اضف كروب 123456789`")

@ABH.on(events.MessageEdited)
async def handle_edited_message(event):
    global report_text, edited_message
    if event.is_group and hasattr(event.original_update, 'message') and event.original_update.message.media:
        edited_message = event.original_update.message
        sender = await event.client.get_entity(edited_message.sender_id)
        message_link = f"https://t.me/c/{str(event.chat_id)[4:]}/{edited_message.id}" 
        # اسم المستخدم، المعرف، والـID
        sender_name = sender.first_name if sender.first_name else "غير معروف"
        sender_username = f"@{sender.username}" if sender.username else "لا يوجد"
        sender_id = sender.id
        report_text = (
            f"🚨 **تم تعديل رسالة في المجموعة**: {event.chat.title}\n"
            f"👤 **المعدل**: {sender_name}\n"
            f"🔗 **المعرف**: {sender_username}\n"
            f"🆔 **الايدي**: `{sender_id}`\n"
            f"📎 [رابط الرسالة المعدلة]({message_link})"
        )
        buttons = [
            [Button.inline("إبلاغ المشرفين", b"notify_admins"), Button.inline("مسح", b"delete_only")]
        ]
        await event.reply("تم تعديل هذه الرسالة", buttons=buttons)

@ABH.on(events.CallbackQuery)
async def callback_handler(event):
    global report_text, edited_message
    try:
        if event.data == b"notify_admins":
            await notify_admins(event)
            buttons = [[Button.inline("مسح", b"delete_only")]]
            await event.edit(buttons=buttons)
        elif event.data == b"delete_only":
            if edited_message:
                await edited_message.delete()
                buttons = [[Button.inline("إبلاغ المشرفين", b"notify_admins")]]
                await event.edit(buttons=None)
                edited_message = None  # إعادة تعيين المتغير بعد حذف الرسالة
            else:
                await event.reply("الرسالة المعدلة غير موجودة.")
    except Exception as e:
        await event.reply(f"حدث خطأ: {str(e)}")

async def notify_admins(event):
    global report_text
    global notification_group_id  # الوصول إلى معرف كروب التبليغ
    if not notification_group_id:
        await event.reply("لم يتم تعيين كروب التبليغ بعد. استخدم الأمر 'اضف كروب <معرف>'.")
        return  # إيقاف التنفيذ هنا إذا لم يكن المعرف موجودًا

    try:
        # إرسال البلاغ إلى كروب التبليغ
        await event.client.send_message(notification_group_id, report_text, link_preview=False)
    except Exception as e:
        await event.reply(f"تعذر إبلاغ كروب التبليغ: {str(e)}")

# تشغيل البوت
ABH.run_until_disconnected()
