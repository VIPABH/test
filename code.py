from telethon import events, types

@ABH.on(events.NewMessage)
async def handler(event):
    # التأكد أن الرسالة تحتوي على ميديا وأنها ملف (فيديو، ملف، بصمة صوتية)
    if event.media and isinstance(event.media, types.MessageMediaDocument):
        video = event.media.document
        
        # استخراج البيانات الأساسية
        file_id = video.id
        access_hash = video.access_hash
        file_reference = video.file_reference
        
        # بناء مرجع المستند
        input_document = types.InputDocument(
            id=file_id,
            access_hash=access_hash,
            file_reference=file_reference
        )
        
        try:
            await ABH.send_file(
                event.chat_id,
                input_document,
                caption="✅ تم إعادة الإرسال بنجاح عبر الـ Hash"
            )
        except Exception as e:
            # هنا يمكنك ربط نظام الـ Error Monitoring الخاص بك
            await ABH.send_message(event.chat_id, f"⚠️ حدث خطأ: {str(e)}")
