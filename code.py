import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# التأكد من المجلد
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

# إعدادات متوافقة مع الـ VPS وسريعة جداً
OPTS = {
    # تحميل أفضل جودة فيديو mp4 وأفضل صوت m4a لضمان سرعة الدمج
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'concurrent_fragment_downloads': 10,
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
    'http_headers': {'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)'},
}

@ABH.on(events.NewMessage)
async def vps_master_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # 1. وقت الاستلام (Latency)
    received_at = time.time()
    latency = round(received_at - e.date.timestamp(), 2)
    
    url = e.text.strip()
    status = await e.reply("📡 **جاري بدء المعالجة...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        # نترك yt-dlp يضيف الامتداد تلقائياً لضمان الدقة
        path_no_ext = os.path.join(DOWNLOAD_DIR, f"v_{u_id}")
        
        # 2. وقت البحث والفحص
        check_start = time.time()
        with yt_dlp.YoutubeDL(OPTS) as ydl:
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            if 'entries' in info: info = info['entries'][0]
            check_time = round(time.time() - check_start, 2)

            # 3. وقت التحميل الفعلي
            await status.edit(f"📥 **جاري التحميل...** (فحص: {check_time}s)")
            dl_start = time.time()
            local_opts = OPTS.copy()
            local_opts['outtmpl'] = f"{path_no_ext}.%(ext)s"
            
            with yt_dlp.YoutubeDL(local_opts) as ydl_dl:
                await asyncio.get_event_loop().run_in_executor(None, lambda: ydl_dl.process_info(info))
            
            dl_time = round(time.time() - dl_start, 2)

        # التأكد من وجود الملف (yt-dlp قد يحفظه بـ mp4 أو mkv)
        actual_file = f"{path_no_ext}.mp4"
        if not os.path.exists(actual_file):
            # بحث عن أي ملف يبدأ بنفس الـ ID في حال اختلف الامتداد
            found_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(f"v_{u_id}")]
            if not found_files: raise Exception("فشل في العثور على الملف المحمل")
            actual_file = os.path.join(DOWNLOAD_DIR, found_files[0])

        # 4. وقت الرفع
        await status.edit(f"📤 **جاري الرفع...** (تحميل: {dl_time}s)")
        up_start = time.time()
        
        attr = [DocumentAttributeVideo(
            duration=int(info.get('duration', 0)),
            w=info.get('width', 1280), h=info.get('height', 720),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, actual_file,
            caption=(
                f"✅ **اكتملت العملية**\n"
                f"📝 `{info.get('title')[:50]}`\n\n"
                f"📡 **الاستلام:** `{latency}s`\n"
                f"🔍 **الفحص:** `{check_time}s`\n"
                f"📥 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{round(time.time() - up_start, 2)}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الإجمالي:** `{round(time.time() - received_at, 2)}s`"
            ),
            attributes=attr,
            supports_streaming=True
        )
        
        await status.delete()
        if os.path.exists(actual_file): os.remove(actual_file)

    except Exception as ex:
        await status.edit(f"⚠️ **خطأ في العملية:**\n`{str(ex)[:150]}`")
