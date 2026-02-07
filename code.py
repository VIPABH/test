from ABH import *
import yt_dlp
import os
import asyncio
import glob
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# دالة تشغيل المهام في Thread منفصل لضمان خفة البوت
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# الإعدادات الأساسية (تحافظ على نظام تسجيل دخولك)
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'extractor_args': {
        'youtube': {'player_client': ['android', 'ios']},
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    status = await e.reply("🔍 جاري فحص الرابط وجلب الجودات المتاحة...")

    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            
            v_id = info['id']
            title = info['title']

        # أزرار اختيار الجودة والصوت
        buttons = [
            [
                Button.inline("🎥 480p", data=f"q|480|{v_id}"),
                Button.inline("🎥 720p", data=f"q|720|{v_id}"),
                Button.inline("🎥 1080p", data=f"q|1080|{v_id}")
            ],
            [
                Button.inline("🎬 أعلى جودة متاحة (Best)", data=f"q|best|{v_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"q|audio|{v_id}")
            ]
        ]
        await status.edit(f"📝 **العنوان:** {title}\n\nاختر الجودة المطلوبة للتحميل:", buttons=buttons)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^q\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    quality = data[1]
    v_id = data[2]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    await e.edit(f"🚀 جاري معالجة طلبك ({quality})...")

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
        opts['merge_output_format'] = 'mp4'
    else:
        # اختيار جودة محددة (مثلاً 720p) مع أفضل صوت متاح
        opts['format'] = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}]/best'
        opts['merge_output_format'] = 'mp4'

    opts['outtmpl'] = f'{unique_path}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            
            # البحث الذكي عن الملف لتجنب خطأ Errno 2
            files = glob.glob(f"{unique_path}*")
            if not files:
                raise FileNotFoundError("فشل النظام في العثور على الملف.")
            
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
            caption=f"✅ **تم التحميل بنجاح ({quality})**\n\n📝 {info.get('title')}",
            reply_to=e.query.msg_id,
            supports_streaming=True,
            attributes=attributes
        )
        
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ فشل التحميل:\n`{str(ex)[:150]}`")
