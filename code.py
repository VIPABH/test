import asyncio
import os
from telethon import events
from faster_whisper import WhisperModel 
from ABH import *

# إعدادات متقدمة للسرعة والدقة
# 1. نستخدم distil-large-v3 لأنه يجمع بين ذكاء الموديلات الكبيرة وسرعة الموديلات الصغيرة
# 2. نحدد cpu_threads=4 لاستغلال كامل قوة المعالج لديك
# 3. نستخدم compute_type="float32" على CPU للحصول على أدق النتائج الممكنة
model = WhisperModel(
    "distil-large-v3", 
    device="cpu", 
    compute_type="float32", 
    cpu_threads=4, 
    num_workers=2
)

@ABH.on(events.NewMessage)
async def handle_audio(event):
    if event.voice or event.audio:
        # تحديد حجم الملف (اختياري: لتجنب تعليق السيرفر بملفات ضخمة)
        if event.file.size > 10 * 1024 * 1024: # 10 ميجا بايت
            return await event.reply("الملف كبير جداً، يرجى إرسال مقطع أقل من 10 دقائق.")

        msg = await event.reply("🚀 جاري المعالجة بأقصى دقة...")
        path = await event.download_media()
        
        try:
            # beam_size=1 مع distil-models يعطي سرعة خارقة ودقة ممتازة
            # task="transcribe" لضمان الكتابة بنفس لغة الصوت
            segments, info = await asyncio.to_thread(
                model.transcribe, 
                path, 
                beam_size=1, 
                language=None, # التعرف التلقائي على اللغة
                vad_filter=True # تصفية الصمت والضوضاء لزيادة السرعة
            )
            
            full_text = "".join([segment.text for segment in segments])

            if not full_text.strip():
                await msg.edit("❌ لم أتمكن من فهم الكلام.")
            else:
                response = (f"**✅ تمت المعالجة بنجاح**\n"
                            f"**اللغة:** {info.language}\n"
                            f"**الدقة:** {info.language_probability:.2%}\n\n"
                            f"**النص:**\n`{full_text.strip()}`")
                await msg.edit(response)
        
        except Exception as e:
            await msg.edit(f"⚠️ خطأ: {str(e)}")
        
        finally:
            if os.path.exists(path):
                os.remove(path)
