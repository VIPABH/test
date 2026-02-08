import yt_dlp
import os
import asyncio
import glob
import time
from ABH import *
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# التأكد من مجلد التنزيل
if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# الإعدادات الشاملة (Universal Options)
ALL_SITES_OPTS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'merge_output_format': 'mp4',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-IG-App-ID': '936619743392459', # لضمان عمل إنستغرام
    },
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'android'],
            'player_skip': ['webpage', 'configs'],
        },
        'tiktok': {
            'app_version': '33.2.3',
        }
    },
}

@ABH.on(events.NewMessage)
async def universal_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🔄 جاري فحص الرابط ومعالجته...")

    # التحقق من نوع الرابط
    is_youtube = any(x in url for x in ["youtube.com", "youtu.be"])
    is_insta = "instagram.com" in url
    
    try:
        # 1. إذا كان يوتيوب: جلب المعلومات وعرض خيارات الجودة
        if is_youtube:
            with yt_dlp.YoutubeDL(ALL_SITES_OPTS) as ydl:
                info = await run_sync(ydl.extract_info, url, False)
                if 'entries' in info: info = info['entries'][0]
                v_id = info['id']
                title = info.get('title', 'Video')
            
            buttons = [
                [Button.inline("🎥 480p", data=f"q|480|{v_id}"), Button.inline("🎥 720p", data=f"q|720|{v_id}")],
                [Button.inline("🎬 أعلى جودة", data=f"q|best|{v_id}"), Button.inline("🎵 صوت MP3", data=f"q|audio|{v_id}")]
            ]
            await status.respond(f"📺 **يوتيوب:** {title[:50]}\n\nاختر الجودة:", buttons=buttons)

        # 2. إذا كان إنستا أو تيك توك أو غيره: تحميل مباشر بأعلى جودة
        else:
            await status.respond("🚀 جاري التحميل المباشر...")
            path = f"downloads/file_{int(time.time())}.mp4"
            opts = ALL_SITES_OPTS.copy()
            opts['outtmpl'] = path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await run_sync(ydl.extract_info, url, True)
            
            await e.respond("📦 جاري الرفع...")
            attr = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
            
            await ABH.send_file(e.chat_id, path, caption=f"✅ **تم التحميل:**\n{info.get('title', '')}", attributes=attr)
            await status.delete()
            if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.respond(f"⚠️ فشل التحميل من هذا الرابط:\n`{str(ex)[:150]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def youtube_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality, v_id = data[1], data[2]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    await e.respond(f"🚀 جاري تحميل يوتيوب جودة {quality}...")
    path = f"downloads/yt_{int(time.time())}"
    opts = ALL_SITES_OPTS.copy()
    
    if quality == "audio":
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
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

        attr = [DocumentAttributeVideo(
            duration=int(info.get('duration', 0)),
            w=info.get('width', 1280), h=info.get('height', 720),
            supports_streaming=True
        )]
        
        await ABH.send_file(e.chat_id, file_path, caption=f"✅ {info.get('title')}", attributes=attr)
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as ex:
        await e.respond(f"⚠️ خطأ يوتيوب:\n`{str(ex)[:100]}`")
