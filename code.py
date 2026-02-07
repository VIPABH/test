from ABH import *
import yt_dlp
import os
import asyncio
from telethon import events, Button

# دالة التشغيل المتزامن
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات السرعة والجودة القصوى
BASE_OPTIONS = {
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['tv', 'web_creator'],
            'player_skip': ['configs', 'webpage']
        }
    },
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # تسريع التحميل عبر استخدام اتصالات متعددة (إذا كان yt-dlp يدعم ذلك بالسيرفر)
    'external_downloader': 'aria2c', 
    'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    text = e.text
    is_url = text.startswith(('http://', 'https://'))
    search_query = text if is_url else f"ytsearch1:{text}"

    status = await e.reply("🔍 جاري جلب البيانات...")

    try:
        # جلب المعلومات فقط في البداية (سريع جداً)
        with yt_dlp.YoutubeDL(BASE_OPTIONS) as ydl:
            info = await run_sync(ydl.extract_info, search_query, False)
            if 'entries' in info: info = info['entries'][0]
            
            video_id = info['id']
            title = info['title']
            url = info['webpage_url']

        # حفظ المعلومات مؤقتاً في الأزرار
        buttons = [
            [
                Button.inline("🎥 فيديو (MP4)", data=f"vid|{video_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"aud|{video_id}")
            ]
        ]
        
        await status.edit(f"✅ تم العثور على:\n**{title}**\n\nاختر صيغة التحميل أدناه:", buttons=buttons)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ في جلب البيانات: `{str(ex)[:100]}`")

@ABH.on(events.CallbackQuery(pattern=r'^(vid|aud)\|'))
async def download_callback(e):
    data = e.data.decode('utf-8').split('|')
    mode = data[0]
    v_id = data[1]
    url = f"https://www.youtube.com/watch?v={v_id}"

    await e.edit("🚀 جاري التحميل بأقصى سرعة...")

    # تخصيص الخيارات بناءً على اختيار المستخدم
    opts = BASE_OPTIONS.copy()
    if mode == 'vid':
        # أفضل جودة فيديو MP4 مدمجة بصوت
        opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        # أفضل جودة صوت فقط
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
            file_path = ydl.prepare_filename(info)
            
            # معالجة الامتداد بعد التحويل
            if mode == 'aud': file_path = file_path.rsplit('.', 1)[0] + '.mp3'
            elif not os.path.exists(file_path):
                base = os.path.splitext(file_path)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    if os.path.exists(f"{base}.{ext}"):
                        file_path = f"{base}.{ext}"; break

        await ABH.send_file(
            e.chat_id, file_path,
            caption=f"✅ تم التحميل بنجاح\n📝 {info['title']}",
            supports_streaming=True
        )
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ فشل التحميل: `{str(ex)[:100]}`")
