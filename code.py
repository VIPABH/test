import yt_dlp
import os
from telethon import events

# إعدادات المجلد
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات yt-dlp الذكية
YDL_OPTIONS = {
    # تحميل أفضل جودة فيديو مدمجة بصوت
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'extractor_args': {
        'youtube': {'player_client': ['android', 'ios']},
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    # تجاهل رسائل البوتات أو الرسائل الفارغة
    if e.is_group and not e.mentioned and not e.is_private:
        return
    
    text = e.text
    if not text or text.startswith(('/', '!', '.')): # تجاهل الأوامر الأخرى
        return

    # تحديد هل المدخل رابط أم نص بحث
    if text.startswith(('http://', 'https://')):
        url = text
        is_search = False
    else:
        url = f"ytsearch1:{text}" # البحث عن نتيجة واحدة فقط
        is_search = True

    status = await e.reply("🔍 جارِ المعالجة..." if not is_search else f"🔎 جارِ البحث عن: **{text}**")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # 1. جلب المعلومات والتحميل
            info = await run_sync(ydl.extract_info, url, download=True)
            
            # إذا كان بحثاً، المعلومات تكون داخل قائمة 'entries'
            video_data = info['entries'][0] if is_search else info
            
            file_path = ydl.prepare_filename(video_data)
            title = video_data.get('title', 'Media')
            
            # التأكد من مسار الملف الفعلي
            if not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm', 'm4v']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"
                        break

        # 2. إرسال الملف
        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بنجاح**\n\n📝 {title}",
            reply_to=e.id,
            supports_streaming=True
        )

        # 3. تنظيف
        await status.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as ex:
        await status.edit(f"⚠️ حدث خطأ:\n`{str(ex)[:100]}`")
