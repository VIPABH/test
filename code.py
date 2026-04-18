import os
import asyncio
from ABH import *
from faster_whisper import WhisperModel

# تحميل الموديل
model = WhisperModel("tiny", device="cpu", compute_type="int8")

@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.voice or e.audio))
async def handler(event):
    # إرسال رسالة انتظار للمستخدم
    status_msg = await event.reply("⏳ جاري تحويل الصوت إلى نص (عربي)...")
    
    # مسار حفظ الملف مؤقتاً
    path = await event.download_media(file="downloads/")
    
    try:
        # إضافة language="ar" لإجبار الموديل على اللغة العربية
        # إضافة task="transcribe" للتأكد من أنه يكتب النص ولا يترجمه للغة أخرى
        segments, info = model.transcribe(path, beam_size=1, language="ar", task="transcribe")
        
        full_text = ""
        for segment in segments:
            full_text += f"{segment.text} "

        if not full_text.strip():
            await status_msg.edit("❌ نعتذر، لم أتمكن من استخراج نص عربي واضح.")
        else:
            # تم إزالة info.language لأننا حددناها مسبقاً بالعربية
            await status_msg.edit(f"✅ **النص المستخرج:**\n\n`{full_text.strip()}`")
            
    except Exception as e:
        await status_msg.edit(f"⚠️ حدث خطأ أثناء المعالجة: {str(e)}")
    
    # تنظيف السيرفر من الملفات المؤقتة
    if os.path.exists(path):
        os.remove(path)

print("--- البوت يعمل الآن (اللغة الافتراضية: العربية) ---")
