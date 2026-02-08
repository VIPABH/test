import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات السرعة القصوى
FAST_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M', '--file-allocation=none'],
    'concurrent_fragment_downloads': 15,
}

def format_time(seconds):
    """تحويل الثواني إلى تنسيق دقيقة:ثانية"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}د {secs}ث" if mins > 0 else f"{secs}ث"

@ABH.on(events.NewMessage)
async def speed_test_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("⚡ **بدء المعالجة الفورية...**")
    
    overall_start = time.time()  # بداية العملية الكلية
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = FAST_OPTS.copy()
        opts['outtmpl'] = path

        # 1. مرحلة استخراج البيانات (Info Extraction)
        info_start = time.time()
        with yt_dlp.YoutubeDL(opts) as ydl:
            # نستخدم download=False أولاً لجلب مدة الفيديو بدقة
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            info_duration = round(time.time() - info_start, 2)
            
            video_len = info.get('duration', 0)
            title = info.get('title', 'بدون عنوان')

            # 2. مرحلة التحميل الفعلي
            await status.edit(f"🔍 فحص: `{info_duration}s`\n📥 جاري التحميل...")
            download_start = time.time()
            await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.download([url]))
            download_duration = round(time.time() - download_start, 2)

        # 3. مرحلة الرفع إلى تيليجرام
        await status.edit(f"📥 تحميل: `{download_duration}s`\n📤 جاري الرفع...")
        upload_start = time.time()
        
        attr = [DocumentAttributeVideo(
            duration=int(video_len),
            w=info.get('width', 720),
            h=info.get('height', 1280),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **اكتملت العملية بنجاح**\n\n"
                f"📝 **العنوان:** {title[:50]}\n"
                f"⏳ **مدة الفيديو:** `{format_time(video_len)}`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🔍 **الفحص:** `{info_duration}s`\n"
                f"📥 **التحميل:** `{download_duration}s`\n"
                f"📤 **الرفع:** `{round(time.time() - upload_start, 2)}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الإجمالي:** `{round(time.time() - overall_start, 2)}s`"
            ),
            attributes=attr,
            supports_streaming=True
        )
        
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:**\n`{str(ex)[:150]}`")
