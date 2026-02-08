import yt_dlp
import os
import asyncio
import glob
import time
from ABH import *
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# إعدادات قوية لتجاوز الحظر بدون كوكيز
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
            'player_client': ['android', 'ios'], # التركيز على تطبيقات الجوال لتجنب حظر الويب
            'player_skip': ['webpage', 'configs'],
        },
        'instagram': {'check_info': True},
        'tiktok': {'app_version': '33.2.3'}
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    text = e.text.strip()
    # التحقق من نوع الرابط
    is_url = text.startswith(('http://', 'https://'))
    url = text if is_url else f"ytsearch1:{text}"
    
    status = await e.reply("🔍 جاري الفحص واستخراج الروابط...")
    
    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            
            # تخزين الرابط الحقيقي بدلاً من ID فقط لدعم المواقع الأخرى
            v_id = info.get('id')
            webpage_url = info.get('webpage_url') 
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
        # حفظ الرابط في قاموس مؤقت أو استخدامه مباشرة إذا كان يوتيوب
        await status.edit(f"📝 **العنوان:** {title}\n\nاختر الجودة المطلوبة:", buttons=buttons)
    except Exception as ex:
        await status.edit(f"⚠️ **فشل جلب البيانات:**\n`{str(ex)[:150]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality, v_id = data[1], data[2]
    
    # محاولة استنتاج الرابط (يعمل مع أغلب المنصات)
    url = f"https://www.youtube.com/watch?v={v_id}" if len(v_id) == 11 else v_id
    
    await e.edit(f"🚀 جاري معالجة التحميل ({quality})...")
    unique_path = f"downloads/{int(time.time())}"
    
    opts = BASE_OPTIONS.copy()
    if quality == "audio":
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    elif quality == "best":
        opts['format'] = 'bestvideo+bestaudio/best'
    else:
        opts['format'] = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}]/best'
    
    opts['outtmpl'] = f'{unique_path}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            files = glob.glob(f"{unique_path}*")
            if not files: raise FileNotFoundError("فشل النظام في إنشاء الملف.")
            file_path = max(files, key=os.path.getctime)

        await e.edit("📦 جاري الرفع إلى تيليجرام...")
        
        attributes = []
        if quality != "audio":
            attributes = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280), h=info.get('height', 720),
                supports_streaming=True
            )]

        await ABH.send_file(
            e.chat_id, file_path,
            caption=f"✅ **تم التحميل:** {info.get('title')}",
            attributes=attributes, supports_streaming=True
        )
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ **خطأ أثناء التحميل:**\n`{str(ex)[:150]}`")
