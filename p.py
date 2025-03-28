async def download_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',  # تحميل الصوت بأعلى جودة
        'quiet': True,  # إخفاء التقدم
        'noplaylist': True,  # عدم تحميل قوائم التشغيل
        'cookiefile': 'cookies.txt',  # إذا كانت الكوكيز مطلوبة
        'noprogress': True,  # إخفاء شريط التقدم
        'default_search': 'ytsearch',  # البحث في يوتيوب
        'outtmpl': '%(id)s.%(ext)s',  # اسم الملف وفقًا لـ ID
        'extractaudio': True,  # استخراج الصوت فقط
        'prefer_ffmpeg': True,  # استخدام FFmpeg إذا كان متاحًا
        'postprocessors': [],  # لا نحتاج إلى معالج إضافي
        'progress_hooks': [lambda d: None],  # إخفاء التقدم بشكل كامل
        'concurrent_fragment_downloads': 100,  # تحميل أجزاء متعددة في وقت واحد
        'max_filesize': 50 * 1024 * 1024,  # الحد الأقصى للحجم (50 ميجابايت)
        'socket_timeout': 30,  # مهلة الاتصال
        'audio_quality': '0',  # تحميل الصوت بأعلى جودة متاحة
        'audio_only': True,  # تحميل الصوت فقط
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)  # استخراج معلومات الفيديو وتحميله
            if 'entries' in info:
                info = info['entries'][0]  # اختر أول نتيجة
            output_file = ydl.prepare_filename(info)  # تحديد اسم الملف
            audio_file = output_file.rsplit('.', 1)[0] + ".mp3"  # التأكد من أنه MP3
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                return audio_file  # إرجاع مسار الملف
            else:
                print(f"Failed to download audio for {query}")
                return None
        except yt_dlp.utils.DownloadError as e:
            print(f"Error: {e}")
            return None
