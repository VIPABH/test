import asyncio
import os
from telethon import events
# إضافة الاستيراد المفقود هنا
from faster_whisper import WhisperModel 
from ABH import *

# تعريف النموذج (يجب تعريفه خارج الدالة لكي لا يتم تحميله في كل مرة يُرسل فيها صوت)
# بما أنك على سيرفر 8GB RAM، نستخدم طراز base مع int8 لضمان السرعة والخفة
model = WhisperModel("base", device="cpu", compute_type="int8")

@ABH.on(events.NewMessage)
async def handle_audio(event):
    # التحقق من وجود صوت أو ملف صوتي
    if event.voice or event.audio:
        msg = await event.reply("جاري التحميل والمعالجة... 🎙")
        
        # تحميل الملف في مسار مؤقت
        path = await event.download_media()
        
        try:
            # المعالجة باستخدام Whisper عبر خيط منفصل (Thread) لعدم تعليق البوت
            segments, info = await asyncio.to_thread(model.transcribe, path, beam_size=5)
            
            full_text = ""
            for segment in segments:
                full_text += f"{segment.text} "

            if not full_text.strip():
                await msg.edit("لم أتمكن من استخراج نص واضح.")
            else:
                response = (f"**اللغة المكتشفة:** {info.language}\n"
                            f"**النص المستخرج:**\n`{full_text.strip()}`")
                await msg.edit(response)
        
        except Exception as e:
            await msg.edit(f"حدث خطأ أثناء المعالجة: {str(e)}")
        
        finally:
            # تنظيف الملفات المؤقتة فور الانتهاء
            if os.path.exists(path):
                os.remove(path)
