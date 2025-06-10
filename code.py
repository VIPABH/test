from telethon import events
import subprocess
import os
import uuid
from ABH import ABH
# مجلدلتنزيلات المؤقت
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# تحميل فيديو أو صوت
def download_from_youtube(url: str, is_audio: bool) -> str:
    out_name = os.path.join(DOWNLOAD_DIR, str(uuid.uuid4()))
    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'outtmpl': f'{out_name}.%(ext)s',
        'noplaylist': True,
    }

    if is_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    else:
        ydl_opts.update({'format': 'bestvideo+bestaudio/best'})

    import yt_dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # العثور على الملف الناتج
    for ext in ['mp3', 'mkv', 'mp4', 'webm']:
        file_path = f"{out_name}.{ext}"
        if os.path.exists(file_path):
            return file_path

    return None

@ABH.on(events.NewMessage(pattern=r'^/yt\s+(https?://\S+)$'))
async def handler_audio(event):
    url = event.pattern_match.group(1)
    await event.reply("🔄 جاري تحميل الصوت...")
    try:
        file_path = download_from_youtube(url, is_audio=True)
        if file_path:
            await event.respond(file= file_path, caption="🎵 تم تحميل الصوت.")
            os.remove(file_path)
        else:
            await event.reply("❌ فشل التحميل.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ:\n{e}")

@ABH.on(events.NewMessage(pattern=r'^/video\s+(https?://\S+)$'))
async def handler_video(event):
    url = event.pattern_match.group(1)
    await event.reply("🔄 جاري تحميل الفيديو...")
    try:
        file_path = download_from_youtube(url, is_audio=False)
        if file_path:
            await event.respond(file= file_path, caption="🎬 تم تحميل الفيديو.")
            os.remove(file_path)
        else:
            await event.reply("❌ فشل التحميل.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ:\n{e}")

print("🤖 Bot is running...")
ABH.run_until_disconnected()
