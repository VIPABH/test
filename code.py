import yt_dlp
import os
import asyncio
import glob
from ABH import *
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# التأكد من وجود مجلد التحميل
if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# إعدادات قوية تدعم جميع المنصات وتتجنب الحظر
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios', 'web'],
            'player_skip': ['webpage', 'configs'],
        },
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    text = e.text.strip()
    # التحقق إذا كان الرابط من يوتيوب أو منصة أخرى
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    
    status = await e.reply("🔍 جاري جلب البيانات من المصدر...")
    
    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            v_id = info.get('id')
            title = info.get('title', 'Video')
            
        buttons = [
            [
                Button.inline("🎥 480p", data=f"q|480|{v_id}"),
                Button.inline("🎥 720p", data=f"q|720|{v_id}"),
                Button.inline("🎥 1080p", data=f"q|1080|{v_id}")
            ],
            [
                Button.inline("🎬 أعلى جودة", data=f"q|best|{v_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"q|audio|{v_id}")
            ]
        ]
        await status.edit(f"📝 **العنوان:** {title}\n\nاختر الصيغة المطلوبة:", buttons=buttons)
    except Exception as ex:
        await status.edit(f"⚠️ **فشل جلب البيانات:**\nتأكد من الرابط أو حاول لاحقاً.\n`{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality = data[1]
    v_id = data[2]
    
    # التعامل مع روابط يوتيوب والروابط المباشرة الأخرى
    url = f"https://www.youtube.com/watch?v={v_id}" if len(v_id) == 11 else v_id
    
    await e.edit(f"🚀 جاري التحميل بمعيار: **{quality}**...")
    
    unique_path = f"downloads/{v_id}_{quality}"
    opts = BASE_OPTIONS.copy()
    
    if quality == "audio":
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif quality == "best":
        opts['format'] = 'bestvideo+bestaudio/best'
    else:
        # محاولة جلب الجودة المطلوبة أو أقرب جودة لها
        opts['format'] = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}]/best'

    opts['outtmpl'] = f'{unique_path}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            files = glob.glob(f"{unique_path}*")
            if not files: raise FileNotFoundError("لم يتم العثور على الملف المحمل.")
            file_path = max(files, key=os.path.getctime)

        await e.edit("📦 جاري الرفع إلى تيليجرام...")
        
        attributes = []
        if quality != "audio":
            attributes = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280),
                h=info.get('height', 720),
                supports_streaming=True
            )]

        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بنجاح**\n\n📝 {info.get('title')}",
            attributes=attributes,
            supports_streaming=True
        )
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        error_msg = str(ex)
        if "Video unavailable" in error_msg:
            msg = "⚠️ الفيديو غير متاح (قد يحتاج كوكيز أو السيرفر محظور)."
        else:
            msg = f"⚠️ فشل التحميل:\n`{error_msg[:150]}`"
        await e.edit(msg)
