import yt_dlp
import os
import asyncio
import glob
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from ABH import *
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# رفع الكفاءة لأقصى حد
executor = ThreadPoolExecutor(max_workers=200)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# إعدادات "السرعة المطلقة" (Absolute Speed)
ULTRA_SPEED_OPTS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'merge_output_format': 'mp4',
    
    # محرك aria2c بإعدادات كسر القيود
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--min-split-size=1M',
        '--max-connection-per-server=16',
        '--split=32',                 # رفع التقسيم لـ 32 لزيادة الضغط
        '--max-tries=5',
        '--retry-wait=2',
        '--connect-timeout=10',
        '--allow-overwrite=true',
    ],
    
    # تفعيل التحميل المتعدد للأجزاء (هذا ما سيجعله سريعاً جداً)
    'concurrent_fragment_downloads': 10, # تحميل 10 أجزاء من الفيديو في نفس اللحظة
    
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-IG-App-ID': '936619743392459',
    },
}

@ABH.on(events.NewMessage)
async def fast_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🚀 **جاري التحميل بأقصى طاقة...**")

    try:
        # استخدام UUID لضمان الخصوصية والسرعة
        u_id = uuid.uuid4().hex[:8]
        path = f"downloads/vid_{u_id}_{int(time.time())}.mp4"
        
        opts = ULTRA_SPEED_OPTS.copy()
        opts['outtmpl'] = path
        
        # إذا كان يوتيوب، سنعطيه خيار الـ Best مباشرة لتقليل وقت "فحص الجودات"
        if "youtube" in url or "youtu.be" in url:
            opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            opts['format'] = 'best'

        # التحميل
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
        
        await status.edit("📤 **جاري الرفع الصاروخي...**")
        
        # استخراج الأبعاد للرفع السريع
        w = info.get('width', 720)
        h = info.get('height', 1280)
        dur = int(info.get('duration', 0))

        await ABH.send_file(
            e.chat_id, path, 
            caption=f"✅ **تم التحميل:** {info.get('title', '')[:50]}",
            attributes=[DocumentAttributeVideo(duration=dur, w=w, h=h, supports_streaming=True)],
            thumb=None # إلغاء الـ Thumb يسرع الرفع
        )
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")
