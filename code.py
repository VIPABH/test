from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events

# دالة run_sync لضمان عدم تعليق البوت
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- إعدادات السرعة الخارقة والجودة الأصلية ---
YDL_OPTIONS = {
    # 'b' تطلب أفضل ملف فيديو مدمج بصوت جاهز من المصدر (أسرع في التحميل والمعالجة)
    'format': 'best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # تفعيل التحميل المتعدد لزيادة السرعة 10 أضعاف
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
    if text.startswith(('http://', 'https://')):
        url = text
        is_search = False
    else:
        url = f"ytsearch1:{text}"
        is_search = True

    status = await e.reply("🚀 جاري المعالجة السريعة...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # التحميل بأقصى سرعة
            info = await run_sync(ydl.extract_info, url, True)
            
            video_data = info['entries'][0] if is_search and 'entries' in info else info
            file_path = ydl.prepare_filename(video_data)
            title = video_data.get('title', 'Media')

            # التأكد من وجود الملف (بسبب اختلاف الصيغ الأصلية)
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm', '3gp', 'm4v']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"
                        break

        # تحديث الحالة للرفع
        await status.edit(f"📦 جاري رفع الفيديو الأصلي:\n**{title[:50]}**")

        # إرسال الفيديو بوضعه الأصلي
        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بأقصى سرعة**\n\n📝 {title}",
            reply_to=e.id,
            supports_streaming=True, # يتيح مشاهدة الفيديو فوراً
            force_document=False    # يرسله كمشغل فيديو وليس ملف مضغوط
        )

        await status.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as ex:
        await status.edit(f"⚠️ حدث خطأ:\n`{str(ex)[:100]}`")
