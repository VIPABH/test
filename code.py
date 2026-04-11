from telethon import events, types
from ABH import ABH  # استيراد العميل الخاص بك

@ABH.on(events.NewMessage)
async def handler(event):
    # التأكد من وجود ميديا في الرسالة
    if not event.media:
        return

    input_media = None

    try:
        # 1. إذا كانت الميديا "مستند" (فيديو، صوت، ملف، ملصق، متحركة)
        if isinstance(event.media, types.MessageMediaDocument):
            doc = event.media.document
            input_media = types.InputDocument(
                id=doc.id,
                access_hash=doc.access_hash,
                file_reference=doc.file_reference
            )

        # 2. إذا كانت الميديا "صورة" (Photo)
        elif isinstance(event.media, types.MessageMediaPhoto):
            photo = event.media.photo
            input_media = types.InputPhoto(
                id=photo.id,
                access_hash=photo.access_hash,
                file_reference=photo.file_reference
            )

        # إرسال الميديا باستخدام الكيان المجهز
        if input_media:
            await ABH.send_file(
                event.chat_id,
                input_media,
                caption="تمت إعادة الإرسال لجميع أنواع الميديا بنجاح ✅"
            )

    except Exception as e:
        # نظام تنبيه الأخطاء (يمكنك ربطه بمصفوفة الأخطاء في بوتك)
        print(f"خطأ في إرسال الميديا: {e}")
        
