import os
import asyncio
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events
from yt_dlp import YoutubeDL
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not os.path.exists("downloads"):
    os.makedirs("downloads")
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'cookiefile': 'cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}
ABH = TelegramClient("x", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)
x = 1
@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def download_audio(event):
    global x
    query = event.pattern_match.group(2)
    ydl = YoutubeDL(YDL_OPTIONS)
    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
    if 'entries' in info and len(info['entries']) > 0:
        info = info['entries'][0]
        print(info)
        file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        await ABH.send_file(
            1910015590,
            file=file_path,
            caption=f"{x}",
            attributes=[
                DocumentAttributeAudio(
                    duration=info.get("duration", 0),
                    title=info.get('title'),
                    performer='ANYMOUS'
                )
            ]
        )
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=False)
        if 'entries' in info and len(info['entries']) > 0:
            video_info = info['entries'][0]
            video_url = video_info.get('webpage_url')
            video_id = video_info.get('id')
            print(f"رابط الفيديو: {video_url}")
            print(f"معرف الفيديو: {video_id}")

        x += 1
        os.remove(file_path)
ABH.run_until_disconnected()
