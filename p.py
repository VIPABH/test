import os
import asyncio
import shutil
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
    'check_formats': False,
    'skip_download': False,
    'writethumbnail': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
        'nopostoverwrites': False,
    }],
}

ABH = TelegramClient("x", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)
x = 1
@ABH.on(events.NewMessage(pattern='يوت|yt (.*)'))
async def download_audio(client, message):
    global x
    query = message.pattern_match.group(1)
    ydl = YoutubeDL(YDL_OPTIONS)
    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
    if 'entries' in info and len(info['entries']) > 0:
        info = info['entries'][0]
        file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        await ABH.send_audio(  
            chat_id=1910015590,
            audio=file_path,
            title=f"ANYMOUS - {info.get('title', 'ABH')}",
            performer=info.get("uploader"),
            reply_to_message_id=message.id, 
            caption=f'{x}'  
        )
        x += 1
        os.remove(file_path)
ABH.run_until_disconnected()
