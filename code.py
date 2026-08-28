from ABH import ABH
from telethon import events

# 1. الـ Handler الأول: يعدل على الحدث
@ABH.on(events.NewMessage)
async def modify_event_handler(event):
    # إضافة الخصائص الخاصة على أوبجكت الحدث
    event.is_done = True
    event.custom_tag = "ABH_PROCESSED"
    event.user_id_str = str(event.sender_id)


# 2. الـ Handler الثاني: يستقبل الحدث المعدل ويرد بدلاً من الطباعة
@ABH.on(events.NewMessage)
async def receive_event_handler(event):
    # قراءة البيانات المعدلة بأمان
    is_done = getattr(event, 'is_done', False)
    custom_tag = getattr(event, 'custom_tag', None)
    
    if is_done:
        response_text = (
            f"<b>تم استقبال حدث معدّل بنجاح!</b>\n\n"
            f"<b>التاج:</b> <code>{custom_tag}</code>\n"
            f"<b>آيدي المستخدم:</b> <code>{event.user_id_str}</code>\n"
            f"<b>الرسالة الأصلية:</b> {event.text}"
        )
    else:
        response_text = f"حدث عادي بدون تعديلات:\n{event.text}"
    
    # الرد المباشر على الرسالة
    await event.reply(response_text, parse_mode='html')
