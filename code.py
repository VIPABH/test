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

# زيادة عدد الخيوط (Threads) للتعامل مع ضغط هائل من المستخدمين
executor = ThreadPoolExecutor(max_workers=50) 

if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# إعدادات السرعة القصوى (Turbo Settings)
ALL_SITES_OPTS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'merge_output_format': 'mp4',
    # تفعيل aria2c للتحميل الصاروخي (يجب أن يكون مثبتاً على السيرفر)
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'X-IG-App-ID': '936619743392459',
    },
    'extractor_args': {
        'youtube': {'player_client': ['ios', 'android'], 'player_skip': ['webpage', 'configs']},
        'tiktok': {'app_version': '33.2.3'},
    },
}

@ABH.on(events.NewMessage)
async def universal_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🔍 جاري الفحص...")

    is_youtube = any(x in url for x in ["youtube.com", "youtu.be"])
    
    try:
        if is_youtube:
            with yt_dlp.YoutubeDL(ALL_SITES_OPTS) as ydl:
                info = await run_sync(ydl.extract_info, url, False)
                if 'entries' in info: info = info['entries'][0]
                v_id = info['id']
                title = info.get('title', 'Video')
            
            buttons = [
                [Button.inline("🎥 480p", data=f"q|480|{v_id}"), Button.inline("🎥 720p", data=f"q|720|{v_id}")],
                [Button.inline("🎬 Best", data=f"q|best|{v_id}"), Button.inline("🎵 MP3", data=f"q|audio|{v_id}")]
            ]
            await status.edit(f"📺 **{title[:50]}**", buttons=buttons)

        else:
            # استخدام UUID لضمان عدم تداخل الملفات عند تعدد المستخدمين
            unique_id = str(uuid.uuid4())[:8]
            path = f"downloads/file_{unique_id}_{int(time.time())}.mp4"
            
            await status.edit("🚀 جاري التحميل بأقصى سرعة...")
            
            opts = ALL_SITES_OPTS.copy()
            opts['outtmpl'] = path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await run_sync(ydl.extract_info, url, True)
            
            await status.edit("📦 جاري الرفع...")
            attr = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
            
            await ABH.send_file(e.chat_id, path, caption=f"✅ {info.get('title', '')}", attributes=attr)
            await status.delete()
            if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ فشل: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def youtube_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality, v_id = data[1], data[2]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    # معرف فريد لكل عملية ضغط زر
    u_id = str(uuid.uuid4())[:8]
    path = f"downloads/yt_{u_id}_{int(time.time())}"
    
    await e.edit(f"🚀 جاري معالجة طلبك ({quality})...")
    
    opts = ALL_SITES_OPTS.copy()
    if quality == "audio":
        opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]})
    elif quality == "best":
        opts['format'] = 'bestvideo+bestaudio/best'
    else:
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
