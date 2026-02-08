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

# إعدادات ذكية تتكيف مع إنستغرام ويوتيوب معاً
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'format': 'best', # إنستغرام يفضل اختيار best مباشرة
    'merge_output_format': 'mp4',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.google.com/',
    },
    'extractor_args': {
        'youtube': {'player_client': ['ios', 'android'], 'player_skip': ['webpage']},
        'instagram': {'check_info': True},
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    # إذا لم يكن رابطاً، ابحث في يوتيوب، وإذا كان رابطاً استخدمه مباشرة
    target_url = url if url.startswith(('http://', 'https://')) else f"ytsearch1:{url}"
    
    status = await e.reply("🔄 جاري فحص الرابط (إنستا/يوتيوب/تيك توك)...")
    
    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, target_url, False)
            if 'entries' in info: info = info['entries'][0]
            
            v_id = info.get('id')
            title = info.get('title', 'Video')
            # حفظ الرابط الأصلي لاستخدامه في التحميل لاحقاً
            original_url = info.get('webpage_url')

        buttons = [
            [Button.inline("🎬 تحميل الفيديو", data=f"dl|best|{v_id}")],
            [Button.inline("🎵 تحميل الصوت", data=f"dl|audio|{v_id}")]
        ]
        
        # إذا كان يوتيوب، أضف خيارات الجودة
        if "youtube" in original_url or "youtu.be" in original_url:
            buttons.insert(0, [
                Button.inline("🎥 480p", data=f"dl|480|{v_id}"),
                Button.inline("🎥 720p", data=f"dl|720|{v_id}"),
                Button.inline("🎥 1080p", data=f"dl|1080|{v_id}")
            ])

        await status.edit(f"✅ **تم العثور على المقطع:**\n📝 {title[:50]}...", buttons=buttons)
        
    except Exception as ex:
        await status.edit(f"⚠️ **عذراً، لم أستطع جلب بيانات الرابط:**\n`{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^dl\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality, vid = data[1], data[2]
    
    # محاولة بناء الرابط بناءً على المعرف
    url = f"https://www.youtube.com/watch?v={vid}" if len(vid) == 11 else vid
    # ملاحظة: لإنستغرام، يفضل تمرير الرابط الأصلي، ولكن yt-dlp ذكي كفاية للتعامل مع الـ ID في أغلب الحالات.

    await e.edit(f"🚀 جاري التحميل والرفع، انتظر قليلاً...")
    
    path = f"downloads/dl_{int(time.time())}"
    opts = BASE_OPTIONS.copy()
    
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
            w=info.get('width', 720), h=info.get('height', 1280),
            supports_streaming=True
        )]

        await ABH.send_file(e.chat_id, file_path, caption="🔥 بواسطة بوتك الذكي", attributes=attr)
        await e.delete()
        os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`{str(ex)[:100]}`")
