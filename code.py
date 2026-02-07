from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events

# --- دالة run_sync لضمان عدم تعليق البوت ---
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- تحسين الإعدادات للسرعة والجودة القصوى ---
YDL_OPTIONS = {
    # 'best' تضمن جودة عالية، و 'ext=mp4' تضمن التوافق مع مشغل تيليجرام
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # محاكاة عملاء يوتيوب الأكثر استقراراً لتفادي 403 Forbidden
    'extractor_args': {
        'youtube': {
            'player_client': ['tv', 'web_creator', 'mweb'],
            'player_skip': ['configs', 'webpage']
        }
    },
    # تسريع التحميل (يتطلب تثبيت aria2 على السيرفر: sudo apt install aria2)
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-k', '1M'],
    'nocheckcertificate': True,
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

    status = await e.reply("🔍 جارِ المعالجة..." if not is_search else f"🔎 جارِ البحث عن: **{text}**")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # التحميل الفعلي
            info = await run_sync(ydl.extract_info, url, True)
            
            video_data = info['entries'][0] if is_search and 'entries' in info else info
            file_path = ydl.prepare_filename(video_data)
            title = video_data.get('title', 'Media')

            # التحقق من المسار النهائي للملف (في حال تحويل الصيغة تلقائياً)
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm', 'm4v']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"
                        break

        # إرسال الملف (مع خاصية streaming لتشغيله أثناء التحميل)
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
