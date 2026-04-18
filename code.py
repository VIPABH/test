import os
import asyncio
from ABH import *
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")

@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.voice or e.audio))
async def handler(event):
    # إرسال رسالة انتظار للمستخدم
    status_msg = await event.reply("⏳ جاري معالجة الصوت وتحويله إلى نص...")
    
    # مسار حفظ الملف مؤقتاً
    path = await event.download_media(file="downloads/")
    
    try:
        # تنفيذ عملية النسخ (Transcribe)
        # beam_size=1 هو الخيار الأسرع للتنفيذ
        segments, info = model.transcribe(path, beam_size=1)
        
        full_text = ""
        for segment in segments:
            full_text += f"{segment.text} "

        if not full_text.strip():
            await status_msg.edit("❌ نعتذر، لم أتمكن من استخراج نص واضح من الفويس.")
        else:
            await status_msg.edit(f"✅ **الترجمة النصية ({info.language}):**\n\n`{full_text.strip()}`")
            
    except Exception as e:
        await status_msg.edit(f"⚠️ حدث خطأ أثناء المعالجة: {str(e)}")
    
    # حذف الملف من السيرفر بعد الانتهاء للحفاظ على المساحة
    if os.path.exists(path):
        os.remove(path)

print("--- البوت يعمل الآن ---")
