from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات ثابتة (تحافظ على نظام تسجيل دخولك الحالي)
YDL_OPTIONS = {
    # تعديل الـ format لطلب النسخة العريضة أولاً وتجنب العمودية
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # السرعة القصوى عبر aria2c
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'extractor_args': {
        # بقاء نظام تسجيل الدخول كما هو (أندرويد و iOS)
        'youtube': {'player_client': ['android', 'ios']},
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    status = await e.reply("🎬 جاري التحميل بالأبعاد الأصلية...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج المعلومات والتحميل
            info = await run_sync(ydl.extract_info, url, True)
            video_data = info['entries'][0] if 'entries' in info else info
            
            file_path = ydl.prepare_filename(video_data)
            
            # جلب البيانات التقنية للفيديو (لضمان المظهر العرضي)
            width = video_data.get('width', 1280)
            height = video_data.get('height', 720)
            duration = int(video_data.get('duration', 0))
            title = video_data.get('title', 'Media')

            # التأكد من مسار الملف النهائي
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"; break

        await status.edit(f"📦 جاري الرفع بنمط الـ Full Screen...\n**{title[:50]}**")

        # الرفع مع إجبار تيليجرام على قراءة الأبعاد الأصلية
        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بالجودة والأبعاد الأصلية**\n\n📝 {title}",
            reply_to=e.id,
            supports_streaming=True,
            attributes=[DocumentAttributeVideo(
                duration=duration,
                w=width,
                h=height,
                supports_streaming=True
            )]
        )

        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await status.edit(f"⚠️ حدث خطأ:\n`{str(ex)[:100]}`")
