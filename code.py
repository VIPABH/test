import asyncio, yt_dlp, json, os, re, uuid
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from Resources import wfffp
from Program import chs
from ABH import ABH, r

# دالة لتشغيل العمليات المتزامنة بشكل غير متزامن
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# دالة التحميل الأساسية
def download_generic(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

# 1. استقبال الأمر وإظهار الأزرار
@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) ?(.*)', from_users=[wfffp]))
async def yt_func(e):
    # استخراج الأمر والمدخلات
    cmd = e.pattern_match.group(1)
    input_str = e.pattern_match.group(2)
    re_msg = await e.get_reply_message()

    if not input_str and re_msg:
        input_str = re_msg.text
    
    if not input_str:
        return await e.reply("🚫 أرسل الرابط أو نص البحث بعد الأمر.")

    # فحص هل المدخل رابط أم نص بحث
    is_url = re.match(r'^https?://', input_str)
    
    if not is_url:
        # البحث في يوتيوب إذا لم يكن رابطاً
        try:
            results = await run_sync(lambda: Y88F8(input_str, max_results=1).to_dict())
            if not results: return await e.reply("❌ لم أجد نتائج لهذا البحث!")
            url = f"https://youtu.be/{results[0]['id']}"
            title = results[0]['title']
        except Exception:
            return await e.reply("❌ حدث خطأ أثناء البحث.")
    else:
        url = input_str
        title = "الرابط المرسل"

    # حل مشكلة حجم بيانات الزر (64 بايت) عبر Redis
    short_id = str(uuid.uuid4())[:8]
    r.setex(f"yt_tmp:{short_id}", 600, url) # صلاحية 10 دقائق

    # إنشاء أزرار الانلاين
    buttons = [
        [
            Button.inline("🎥 تحميل فيديو", data=f"dl_v|{short_id}"),
            Button.inline("🎵 تحميل صوت (MP3)", data=f"dl_a|{short_id}")
        ]
    ]
    
    await e.reply(f"**🎬 العنوان:** `{title}`\n\nاختر نوع الملف الذي تريده:", buttons=buttons)

# 2. معالجة ضغطات الأزرار والتحميل
@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def callback_dl(e):
    data = e.data.decode("utf-8").split("|")
    type_dl = data[0]  # dl_v أو dl_a
    short_id = data[1]
    
    # جلب الرابط من الذاكرة
    url = r.get(f"yt_tmp:{short_id}")
    if not url:
        return await e.answer("⚠️ انتهت صلاحية الطلب، أرسل الرابط من جديد.", alert=True)
    
    url = url.decode("utf-8") if isinstance(url, bytes) else url
    
    await e.edit("⏳ جاري المعالجة والتحميل...")

    # إعدادات yt-dlp الصامتة
    ydl_ops = {
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "quiet": True,
        "no_warnings": True,
        "logger": None,
        "outtmpl": f"downloads/{e.sender_id}_%(title)s.%(ext)s",
    }

    if type_dl == "dl_v":
        # إعدادات الفيديو
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    else:
        # إعدادات الصوت والتحويل لـ MP3
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        # تنفيذ التحميل
        info = await run_sync(download_generic, ydl_ops, url)
        file_path = info.get('filepath') or info['requested_downloads'][0]['filepath']
        
        # تصحيح الامتداد في حالة الصوت
        if type_dl == "dl_a" and not file_path.endswith(".mp3"):
            new_path = os.path.splitext(file_path)[0] + ".mp3"
            if os.path.exists(new_path): file_path = new_path

        title = info.get("title", "File")
        duration = info.get("duration", 0)
        performer = info.get("uploader", "Downloader")

        # إرسال الملف
        attributes = []
        if type_dl == "dl_a":
            attributes = [DocumentAttributeAudio(duration=int(duration), title=title, performer=performer)]

        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"**✅ تم التحميل بنجاح**\n\n[{title}]({url})",
            attributes=attributes,
            supports_streaming=True if type_dl == "dl_v" else False
        )
        
        # التنظيف
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"❌ **فشل التحميل:**\n`{str(ex)[:150]}`")
