from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events

# --- الجزء المفقود: تعريف دالة run_sync ---
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)
# ------------------------------------------

if not os.path.exists("downloads"):
    os.makedirs("downloads")

YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': False, # اجعلها False مؤقتاً لنرى إذا نجح التخطي
    'extractor_args': {
        'youtube': {
            # استخدام عملاء الـ TV و Web_Creator يتخطى طلب الـ PO Token حالياً
            'player_client': ['tv', 'web_creator', 'mweb'],
            'player_skip': ['configs', 'webpage']
        }
    },
    # إضافة User-Agent متوافق مع متصفحات الجوال العادية
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
@ABH.on(events.NewMessage)
async def smart_downloader(e):
    # تجاهل الأوامر التي تبدأ بـ / أو ! لعدم تداخل المهام
    if not e.text or e.text.startswith(('/', '!', '.')):
        return
    
    # منع البوت من الرد على نفسه أو البوتات الأخرى
    if e.sender and e.sender.bot:
        return

    text = e.text

    # تحديد هل هو رابط أم بحث نصي
    if text.startswith(('http://', 'https://')):
        url = text
        is_search = False
    else:
        url = f"ytsearch1:{text}"
        is_search = True

    status = await e.reply("🔍 جارِ الفحص..." if not is_search else f"🔎 جارِ البحث عن: **{text}**")

    try:
        # استخدام yt-dlp داخل run_sync لمنع تعليق البوت
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # جلب المعلومات والتحميل
            info = await run_sync(ydl.extract_info, url, True)
            
            # إذا كان بحثاً، البيانات تكون داخل entries
            video_data = info['entries'][0] if is_search and 'entries' in info else info
            
            file_path = ydl.prepare_filename(video_data)
            title = video_data.get('title', 'Media')

            # تصحيح مسار الملف في حال تغير الامتداد (مثلاً من mp4 إلى mkv)
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm', 'm4v']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"
                        break

        # إرسال الملف المكتمل
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
