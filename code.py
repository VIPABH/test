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

# الإعدادات النهائية للأداء المطلق
FINAL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--max-connection-per-server=16',
        '--split=16',
        '--min-split-size=1M',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        '--max-overall-download-limit=0',
        '--async-dns=false',  # أحياناً الـ DNS يبطئ البداية
        '--stream-piece-selector=random', # اختيار عشوائي للأجزاء لتمويه السيرفر
    ],
    'concurrent_fragment_downloads': 20,
    # إضافة هذا السطر الهام جداً لتجاوز تضييق السرعة في يوتيوب
    'params': {'n_sig_check': False}, 
}
def format_time(seconds):
    if seconds < 60: return f"{int(seconds)}ث"
    return f"{int(seconds//60)}د {int(seconds%60)}ث"

@ABH.on(events.NewMessage)
async def ultimate_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    msg_text = e.text.strip()
    # إذا لم يكن رابطاً، سنقوم بالبحث في يوتيوب تلقائياً
    url = msg_text if msg_text.startswith(('http://', 'https://')) else f"ytsearch1:{msg_text}"
    
    status = await e.reply("🚀 **جاري التنفيذ...**")
    overall_start = time.time()
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = FINAL_OPTS.copy()
        opts['outtmpl'] = path

        # 1. استخراج وفحص (تم دمج العمليات لربح الوقت)
        info_start = time.time()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if 'entries' in info: info = info['entries'][0] # في حال كان بحثاً
            
            info_duration = round(time.time() - info_start, 2)
            video_len = info.get('duration', 0)
            title = info.get('title', 'بدون عنوان')

        # 2. الرفع (مع حساب الوقت الحقيقي)
        upload_start = time.time()
        attr = [DocumentAttributeVideo(
            duration=int(video_len),
            w=info.get('width', 720), h=info.get('height', 1280),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **اكتملت العملية بنجاح**\n\n"
                f"📝 **العنوان:** {title[:60]}...\n"
                f"⏳ **مدة الفيديو:** `{format_time(video_len)}`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🔍 **الفحص والتحميل:** `{info_duration}s`\n"
                f"📤 **الرفع:** `{round(time.time() - upload_start, 2)}s`\n"
                f"🚀 **الإجمالي:** `{round(time.time() - overall_start, 2)}s`"
            ),
            attributes=attr,
            supports_streaming=True
        )
        
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:** `{str(ex)[:100]}`")
