from telethon import types, events
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(pattern="تيست"))
async def test(e):
    r = await e.get_reply_message()
    
    if not r:
        await e.reply("عذراً، يجب أن ترد على رسالة معينة لاستخدام هذا الأمر.")
        return

    # نقوم بجلب الرسالة من السيرفر مباشرة لضمان الحصول على كائن 'replies' الكامل
    # نستخدم get_messages مع معرف الرسالة ومعرف المحادثة
    full_message = await e.client.get_messages(e.chat_id, ids=r.id)

    # التحقق من وجود كائن الردود
    if full_message.replies:
        count = full_message.replies.replies
        await e.reply(f"عدد الردود الفعلي على هذه الرسالة هو: {count}")
    else:
        # إذا كانت القيمة None، قد يعني ذلك أنها رسالة لا تحتوي على خيار الردود
        await e.reply("لم يتم العثور على أي ردود مرتبطة بهذه الرسالة في السيرفر.")
