from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# --- دالة تشغيل المهام الثقيلة في Thread منفصل لعدم تعليق البوت ---
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# إنشاء مجلد التحميل إذا لم يكن موجوداً
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- الإعدادات الأساسية (نفس نظام دخولك الحالي مع تحسين السرعة) ---
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # السرعة التوربينية (تطلب تثبيت aria2 في السيرفر)
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'extractor_args': {
        'youtube': {'player_client': ['android', 'ios']},
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    # تجاهل الأوامر والرسائل من البوتات
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    # التمييز بين الرابط والبحث النصي
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    
    status = await e.reply("🔍 جاري جلب أفضل جودة متاحة...")

    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            # جلب معلومات الفيديو فقط (سريع جداً)
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            
            v_id = info['id']
            title = info['title']
            duration = info.get('duration', 0)

        # أزرار اختيار النوع
        buttons = [
            [
                Button.inline("🎥 فيديو (أعلى جودة)", data=f"v|{v_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"a|{v_id}")
            ]
        ]
        await status.edit(f"📝 **العنوان:** {title}\n⏱ **المدة:** {duration} ثانية\n\nاختر الصيغة المطلوبة:", buttons=buttons)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ في جلب البيانات: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    mode = data[0]
    v_id = data[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    await e.edit("🚀 جاري التحميل بالجودة الأصلية...")

    opts = BASE_OPTIONS.copy()
    if mode == 'v':
        # طلب أعلى جودة فيديو وصوت مدمجين (حتى 4K إذا توفرت)
        opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4' # لضمان التوافق
    else:
        # طلب أفضل جودة صوت فقط وتحويلها لـ MP3
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    opts['outtmpl'] = f'downloads/{v_id}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            # التحميل الفعلي
            info = await run_sync(ydl.extract_info, url, True)
            file_path = ydl.prepare_filename(info)
            
            # تصحيح مسار الملف بناءً على الصيغة النهائية
            if mode == 'a': 
                file_path = file_path.rsplit('.', 1)[0] + '.mp3'
            elif not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"; break

        await e.edit("📦 جاري الرفع إلى تيليجرام...")

        # تجهيز سمات الفيديو (الأبعاد والمدة) لضمان العرض الصحيح
        attributes = []
        if mode == 'v':
            attributes = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280),
                h=info.get('height', 720),
                supports_streaming=True
            )]

        # إرسال الملف النهائي
        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"✅ **تم التحميل بنجاح**\n\n📝 {info['title']}",
            reply_to=e.query.msg_id,
            supports_streaming=True,
            attributes=attributes
        )
        
        await e.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ فشل التحميل: `{str(ex)[:100]}`")
