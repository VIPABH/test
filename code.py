from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events
from telethon.tl.types import DocumentAttributeVideo # لإضافة أبعاد الفيديو

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

YDL_OPTIONS = {
    # 'bestvideo+bestaudio' تضمن جلب النسخة الأصلية العريضة وليس نسخة الجوال العمودية
    # نستخدم /best لضمان وجود خيار بديل في حال فشل الدمج
    'format': 'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'extractor_args': {
        'youtube': {'player_client': ['tv', 'web_creator']}, # عملاء الـ TV يضمنون الصيغة العرضية
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    status = await e.reply("🎬 جاري جلب الفيديو بالأبعاد الأصلية...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            video_data = info['entries'][0] if 'entries' in info else info
            file_path = ydl.prepare_filename(video_data)
            
            # استخراج أبعاد الفيديو الأصلية
            width = video_data.get('width')
            height = video_data.get('height')
            duration = int(video_data.get('duration', 0))
            title = video_data.get('title', 'Media')

            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"; break

        await status.edit(f"📦 جاري رفع الفيديو...\n**{title[:50]}**")

        # إرسال الفيديو مع تحديد الأبعاد ليظهر بشكل صحيح
        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بالأبعاد الأصلية**\n\n📝 {title}",
            reply_to=e.id,
            supports_streaming=True,
            # إضافة سمات الفيديو لضمان ظهوره بشكل عرضي أو طولي حسب الأصل
            attributes=[DocumentAttributeVideo(
                duration=duration,
                w=width if width else 1280,
                h=height if height else 720,
                supports_streaming=True
            )] if width and height else None
        )

        await status.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await status.edit(f"⚠️ حدث خطأ:\n`{str(ex)[:100]}`")
