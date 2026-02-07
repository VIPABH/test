from ABH import *
import yt_dlp
import os
import asyncio
import time
from telethon import events

# دالة run_sync لضمان عدم تعليق البوت
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# دالة مخصصة لعرض تقدم التحميل (عداد السرعة)
def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        s = d.get('_speed_str', '0Mbps')
        t = d.get('_eta_str', '00:00')
        # سيتم طباعة التقدم في التيرمينال، ويمكن تطويره ليتحدث في تيليجرام لاحقاً
        print(f"📥 التحميل: {p} | السرعة: {s} | الوقت المتبقي: {t}")

YDL_OPTIONS = {
    # الجودة الأفضل والمتوافقة مع تيليجرام
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'progress_hooks': [progress_hook], # تفعيل العداد
    'extractor_args': {
        'youtube': {'player_client': ['android', 'ios']},
    },
    # تسريع التحميل باستخدام تعدد الاتصالات (Multi-threading)
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    if text.startswith(('http://', 'https://')):
        url = text
        is_search = False
    else:
        url = f"ytsearch1:{text}"
        is_search = True

    status = await e.reply("🔍 جارِ الفحص..." if not is_search else f"🔎 جارِ البحث عن: **{text}**")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # التحميل الفعلي باستخدام run_sync
            info = await run_sync(ydl.extract_info, url, True)
            
            video_data = info['entries'][0] if is_search and 'entries' in info else info
            file_path = ydl.prepare_filename(video_data)
            title = video_data.get('title', 'Media')

            # التأكد من المسار النهائي
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm', 'm4v']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"
                        break

        # تحديث الرسالة قبل الرفع
        await status.edit(f"🚀 اكتمل التحميل!\n📦 جاري رفع: **{title[:50]}**")

        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بنجاح**\n\n📝 {title}",
            reply_to=e.id,
            supports_streaming=True
        )

        await status.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as ex:
        await status.edit(f"⚠️ حدث خطأ:\n`{str(ex)[:100]}`")
