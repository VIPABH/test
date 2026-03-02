import asyncio
import os
from telethon import events
from playwright.async_api import async_playwright
from ABH import *
@ABH.on(events.NewMessage)
async def handle_audio(event):
    # التحقق من وجود صوت أو ملف صوتي
    if event.voice or event.audio:
        msg = await event.reply("جاري التحميل والمعالجة... 🎙")
        
        # تحميل الملف في مسار مؤقت
        path = await event.download_media()
        
        try:
            # المعالجة باستخدام Whisper
            # beam_size=5 يعطي دقة توازن بين السرعة والذكاء
            segments, info = await asyncio.to_thread(model.transcribe, path, beam_size=5)
            
            full_text = ""
            for segment in segments:
                full_text += f"{segment.text} "

            if not full_text.strip():
                await msg.edit("لم أتمكن من استخراج نص واضح.")
            else:
                response = (f"**اللغة المكتشفة:** {info.language}\n"
                            f"**النص:**\n`{full_text.strip()}`")
                await msg.edit(response)
        
        except Exception as e:
            await msg.edit(f"حدث خطأ أثناء المعالجة: {str(e)}")
        
        finally:
            # تنظيف الملفات المؤقتة
            if os.path.exists(path):
                os.remove(path)
