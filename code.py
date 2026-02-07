from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# دالة تشغيل المهام الثقيلة لضمان عدم تعليق البوت
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- الإعدادات المحسنة للجودة الفائقة والسرعة ---
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'external_downloader': 'aria2c',
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
    'extractor_args': {
        'youtube': {'player_client': ['android', 'ios']}, # نظام دخولك الحالي
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    
    status = await e.reply("🔍 جاري فحص أعلى جودة متاحة...")

    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            
            v_id = info['id']
            title = info['title']
            # جلب الجودات المتوفرة للعرض (اختياري)
            duration = info.get('duration', 0)

        buttons = [
            [
                Button.inline("🎥 فيديو بأعلى دقة (4K/HD)", data=f"v|{v_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"a|{v_id}")
            ]
        ]
        await status.edit(f"📝 **العنوان:** {title}\n⏱ **المدة:** {duration} ثانية\n\nاختر الصيغة المطلوبة:", buttons=buttons)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    mode = data[0]
    v_id = data[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    
    await e.edit("🚀 جاري تحميل الجودة الفائقة... انتظر قليلاً")

    opts = BASE_OPTIONS.copy()
    if mode == 'v':
        # التعديل الجوهري: نطلب أفضل فيديو (مهما كانت الدقة) + أفضل صوت
        # ونحدد mp4 كحاوية نهائية لضمان التوافق مع تيليجرام
        opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4' 
    else:
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    opts['outtmpl'] = f'downloads/{v_id}.%(ext)s'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            expected_filename = ydl.prepare_filename(info)
            
            # الصائد الذكي للملفات لتفادي خطأ Errno 2
            file_path = expected_filename
            if mode == 'a':
                file_path = os.path.splitext(expected_filename)[0] + ".mp3"
            
            if not os.path.exists(file_path):
                for f in os.listdir("downloads"):
                    if f.startswith(v_id):
                        file_path = os.path.join("downloads", f)
                        break

        await e.edit("📦 جاري الرفع بجودة HD...")

        attributes = []
        if mode == 'v':
            # نرسل الأبعاد الأصلية (مثلاً 1920x1080) لضمان عدم ضغط تيليجرام للفيديو
            attributes = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1920), 
                h=info.get('height', 1080),
                supports_streaming=True
            )]

        await ABH.send_file(
            e.chat_id,
            file_path,
            caption=f"🎬 **تم التحميل بأعلى جودة متوفرة**\n\n📝 {info.get('title')}",
            reply_to=e.query.msg_id,
            supports_streaming=True,
            attributes=attributes
        )
        
        await e.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ فشل في معالجة الجودة العالية:\n`{str(ex)[:150]}`")
