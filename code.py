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

# إعدادات السرعة الخام (Raw Speed)
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

@ABH.on(events.NewMessage)
async def fast_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("⚡ **بدء العمل...**")
    
    start_time = time.time() # بداية الوقت الكلي
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = FAST_OPTS.copy()
        opts['outtmpl'] = path

        # --- مرحلة التحميل ---
        download_start = time.time()
        with yt_dlp.YoutubeDL(opts) as ydl:
            # التحميل المباشر بدون فحص مسبق لربح الثواني
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        download_end = time.time()
        
        dl_duration = round(download_end - download_start, 2)
        await status.edit(f"📥 تم التحميل في: `{dl_duration}` ثانية\n📤 جاري الرفع...")

        # --- مرحلة الرفع ---
        upload_start = time.time()
        
        attr = [DocumentAttributeVideo(
            duration=int(info.get('duration', 0)),
            w=info.get('width', 720),
            h=info.get('height', 1280),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, path,
            caption=f"✅ **تمت العملية بنجاح**\n\n⏱ التحميل: `{dl_duration}s`\n⏱ الرفع: `{round(time.time() - upload_start, 2)}s`",
            attributes=attr,
            supports_streaming=True
        )
        
        upload_end = time.time()
        total_duration = round(upload_end - start_time, 2)

        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")
