from ABH import *
import yt_dlp
import os
import asyncio
import glob
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

# دالة تشغيل المهام الثقيلة
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# الإعدادات الأساسية
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
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
    url = text if text.startswith(('http://', 'https://')) else f"ytsearch1:{text}"
    status = await e.reply("🔍 جاري جلب البيانات...")
    try:
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            if 'entries' in info: info = info['entries'][0]
            v_id, title = info['id'], info['title']
        buttons = [[Button.inline("🎥 فيديو أعلى جودة", data=f"v|{v_id}"),
                    Button.inline("🎵 صوت MP3", data=f"a|{v_id}")]]
        await status.edit(f"📝 **العنوان:** {title}\n\nاختر الصيغة:", buttons=buttons)
    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    mode, v_id = data[0], data[1]
    url = f"https://www.youtube.com/watch?v={v_id}"
    await e.edit("🚀 جاري التحميل والمعالجة...")

    # تعديل المسار ليكون فريداً لكل عملية لتجنب Errno 2
    unique_path = f"downloads/{v_id}_{mode}"
    opts = BASE_OPTIONS.copy()
    
    if mode == 'v':
        opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4'
        opts['outtmpl'] = f'{unique_path}.%(ext)s'
    else:
        opts['format'] = 'bestaudio/best'
        opts['outtmpl'] = f'{unique_path}.%(ext)s'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await run_sync(ydl.extract_info, url, True)
            
            # --- البحث الذكي عن الملف باستخدام glob ---
            # هذا السطر يحل مشكلة Errno 2 نهائياً بالبحث عن أي ملف يبدأ بـ unique_path
            files = glob.glob(f"{unique_path}*")
            if not files:
                raise FileNotFoundError("فشل النظام في العثور على الملف المحمل.")
            
            # نختار الملف الذي انتهى منه التحميل (الأحدث أو الأكبر)
            file_path = max(files, key=os.path.getctime)

        await e.edit("📦 جاري الرفع بجودة عالية...")

        attributes = []
        if mode == 'v':
            attributes = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1920),
                h=info.get('height', 1080),
                supports_streaming=True
            )]

        await ABH.send_file(
            e.chat_id, file_path,
            caption=f"✅ **تم التحميل بنجاح**\n\n📝 {info.get('title')}",
            reply_to=e.query.msg_id,
            supports_streaming=True,
            attributes=attributes
        )
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ فشل:\n`{str(ex)[:150]}`")
