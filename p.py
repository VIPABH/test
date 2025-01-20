from telethon import TelegramClient, events, Button
import os
from database import save_notification_group, get_notification_group, delete_notification_group

# الحصول على متغيرات البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تهيئة عميل البوت
ABH = TelegramClient('c', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern=r'^اضف كروب (\d+)$'))
async def add_group(event):
    match = event.pattern_match  # استخراج الرقم من الأمر
    if match:
        notification_group_id = int(match.group(1))
        group_id = event.chat_id  # الحصول على معرف المجموعة الحالية
        save_notification_group(group_id, notification_group_id)  # تخزين في قاعدة البيانات
        await event.reply(f"تم تعيين الكروب بمعرف: {notification_group_id} ككروب التبليغ.")
    else:
        await event.reply("يرجى إدخال معرف كروب صحيح. مثال: `اضف كروب 123456789`")

@ABH.on(events.NewMessage(pattern=r'^احذف كروب$')) 
async def delete_group(event):
    group_id = event.chat_id  # الحصول على معرف المجموعة الحالية
    # محاولة حذف الكروب من قاعدة البيانات
    result = delete_notification_group(group_id)
    if result:
        await event.reply(f"تم حذف الكروب من قاعدة البيانات.")
    else:
        await event.reply("لا يوجد كروب تم تعيينه لهذه المجموعة.")

@ABH.on(events.MessageEdited)
async def handle_edited_message(event):
    if event.is_group and hasattr(event.original_update, 'message') and event.original_update.message.media:
        edited_message = event.original_update.message
        sender = await event.client.get_entity(edited_message.sender_id)
        message_link = f"https://t.me/c/{str(event.chat_id)[4:]}/{edited_message.id}" 
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

        # جلب معرف كروب التبليغ من قاعدة البيانات
        notification_group_id = get_notification_group(event.chat_id)
        if notification_group_id:
            # إرسال البلاغ فورًا إلى كروب التبليغ
            try:
                await event.client.send_message(notification_group_id, report_text, link_preview=False)
                await event.reply("تم إبلاغ المشرفين في كروب التبليغ.")
            except Exception as e:
                await event.reply(f"تعذر إرسال البلاغ إلى كروب التبليغ: {str(e)}")
        else:
            await event.reply("لم يتم تعيين كروب التبليغ لهذه المجموعة. استخدم الأمر 'اضف كروب <معرف>' لتعيينه.")

ABH.run_until_disconnected()
