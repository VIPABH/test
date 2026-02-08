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

# رفع عدد الخيوط لـ 100 لاستغلال قوة السيرفر بالكامل
# هذا يسمح بمعالجة 100 طلب تحميل ودمج في نفس اللحظة
executor = ThreadPoolExecutor(max_workers=100)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# إعدادات الاستغلال الكامل للموارد
MAX_PERFORMANCE_OPTS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'merge_output_format': 'mp4',
    
    # إعدادات aria2c المتوحشة: 16 اتصال لكل سيرفر، 16 اتصال للملف الواحد
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--min-split-size=1M',
        '--max-connection-per-server=16',
        '--split=16',
        '--max-overall-download-limit=0', # سرعة غير محدودة
        '--file-allocation=none' # تخطي حجز المساحة لبدء التحميل فوراً
    ],
    
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-IG-App-ID': '936619743392459',
    },
    'extractor_args': {
        'youtube': {'player_client': ['ios', 'android'], 'player_skip': ['webpage', 'configs']},
        'tiktok': {'app_version': '33.2.3'},
    },
    'buffersize': 1024 * 1024 * 16, # زيادة حجم البافر لـ 16 ميجا لتسريع الكتابة على القرص
}

@ABH.on(events.NewMessage)
async def extreme_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("⚡ **جاري المعالجة الفورية...**")

    is_youtube = any(x in url for x in ["youtube.com", "youtu.be"])
    
    try:
        if is_youtube:
            with yt_dlp.YoutubeDL(MAX_PERFORMANCE_OPTS) as ydl:
                info = await run_sync(ydl.extract_info, url, False)
                if 'entries' in info: info = info['entries'][0]
                v_id = info['id']
                title = info.get('title', 'Video')
            
            buttons = [
                [Button.inline("🎥 1080p", data=f"q|1080|{v_id}"), Button.inline("🎥 720p", data=f"q|720|{v_id}")],
                [Button.inline("🎬 بأعلى جودة", data=f"q|best|{v_id}"), Button.inline("🎵 صوت MP3", data=f"q|audio|{v_id}")]
            ]
            await status.edit(f"📺 **{title[:60]}**", buttons=buttons)

        else:
            # التحميل المباشر للمنصات الأخرى (انستا، تيك توك) باستخدام UUID
            u_id = uuid.uuid4().hex[:10]
            path = f"downloads/ext_{u_id}_{int(time.time())}.mp4"
            
            await status.edit("🚀 **بدء التحميل الصاروخي...**")
            
            opts = MAX_PERFORMANCE_OPTS.copy()
            opts['outtmpl'] = path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await run_sync(ydl.extract_info, url, True)
            
            await status.edit("📦 **جاري الرفع السريع...**")
            
            # الرفع باستخدام الموارد المتاحة
            await ABH.send_file(
                e.chat_id, path, 
                caption=f"✅ {info.get('title', '')}",
                attributes=[DocumentAttributeVideo(
                    duration=int(info.get('duration', 0)),
                    w=info.get('width', 720), h=info.get('height', 1280),
                    supports_streaming=True
                )]
            )
            await status.delete()
            if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ فشل: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def youtube_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality, v_id = data[1], data[2]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    u_id = uuid.uuid4().hex[:10]
    path = f"downloads/yt_{u_id}_{int(time.time())}"
    
    await e.edit(f"🚀 **جاري سحب الجودة {quality}...**")
    
    opts = MAX_PERFORMANCE_OPTS.copy()
    if quality == "audio":
        opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]})
    elif quality == "best":
        opts['format'] = 'bestvideo+bestaudio/best'
    else:
        # جلب الجودة المحددة مع ضمان الدمج بأسرع طريقة
        opts['format'] = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best'
    
    opts['outtmpl'] = f'{path}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            files = glob.glob(f"{path}*")
            file_path = max(files, key=os.path.getctime)

        await ABH.send_file(e.chat_id, file_path, caption=f"✅ {info.get('title')}", supports_streaming=True)
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as ex:
        await e.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")
