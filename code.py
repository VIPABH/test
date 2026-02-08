import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# الإعدادات لكسر سرعة 33KiB اللعينة
FORCE_SPEED_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # التعديل الجوهري: إجبار يوتيوب على معاملتنا كجهاز فحص أندرويد
    'extractor_args': {
        'youtube': {
            'player_client': ['android_test', 'android', 'ios'],
            'player_skip': ['webpage', 'configs'],
        }
    },
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--max-connection-per-server=16',
        '--split=16',
        '--min-split-size=100K', # تقليل الحجم الأدنى للتقسيم ليتم تقسيم حتى الملفات الصغيرة
        '--stream-piece-selector=random',
    ],
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro) gzip',
    },
}

@ABH.on(events.NewMessage)
async def god_speed_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🚀 **جاري كسر قيود السرعة...**")
    start_time = time.time()
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/speed_{u_id}.mp4"
        
        opts = FORCE_SPEED_OPTS.copy()
        opts['outtmpl'] = path

        # التحميل
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if 'entries' in info: info = info['entries'][0]

        # الرفع
        upload_start = time.time()
        await ABH.send_file(
            e.chat_id, path,
            caption=f"✅ **تم كسر القيود بنجاح**\n⏱ التحميل: `{round(upload_start - start_time, 2)}s`",
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
        )
        await status.delete()
        os.remove(path) if os.path.exists(path) else None

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:** `{str(ex)[:100]}`")
