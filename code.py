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

# الإعدادات المتوافقة مع قيود السيرفر وسرعة aria2c
FINAL_ULTRA_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    
    'extractor_args': {
        'youtube': {'player_client': ['android_test'], 'player_skip': ['webpage']}
    },
    
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--max-connection-per-server=16',
        '--split=16',
        '--min-split-size=1M',  # تم التعديل لـ 1 ميغا لتجنب الخطأ
        '--max-overall-download-limit=0',
        '--file-allocation=none',
        '--no-conf',
    ],
    'concurrent_fragment_downloads': 15,
    'buffersize': 1024 * 1024 * 16,
}

@ABH.on(events.NewMessage)
async def stable_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🚀 **جاري التحميل بأقصى سرعة متاحة...**")
    
    start_time = time.time()
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = FINAL_ULTRA_OPTS.copy()
        opts['outtmpl'] = path

        with yt_dlp.YoutubeDL(opts) as ydl:
            # التحميل المباشر
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        dl_time = round(time.time() - start_time, 2)
        
        # معلومات الفيديو
        video_len = info.get('duration', 0)
        title = info.get('title', 'بدون عنوان')

        await status.edit(f"📥 **اكتمل التحميل:** `{dl_time}s`\n📤 **جاري الرفع...**")

        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **تم التحميل بنجاح**\n"
                f"📝 {title[:50]}\n"
                f"⏱ وقت التحميل: `{dl_time}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(video_len),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
        )
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:**\n`{str(ex)[:150]}`")
