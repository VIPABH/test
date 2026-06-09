from telethon import types, events
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(pattern="تيست"))
async def test(e):
    # جلب الرسالة التي تم الرد عليها
    r = await e.get_reply_message()
    
    # التحقق من أن المستخدم قام بعمل "رد" (Reply) فعلاً
    if not r:
        await e.edit("عذراً، يجب أن ترد على رسالة معينة لاستخدام هذا الأمر.")
        return

    # التحقق مما إذا كانت الرسالة تحتوي على ردود (replies)
    # ملاحظة: في حال لم يكن هناك أي رد على الرسالة، قد تكون قيمة r.replies هي None
    if r.replies and r.replies.replies:
        count = r.replies.replies
        await e.edit(f"عدد الردود على هذه الرسالة هو: {count}")
    else:
        await e.edit("لا توجد ردود على هذه الرسالة حالياً.")
