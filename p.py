import os
import asyncio
import shutil
from pyrogram import Client, filters
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

final = Client("youtube_audio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
@final.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("مرحباً! أرسل:\n\nيوت + اسم الأغنية")
x = 1
@final.on_message(filters.regex(r"^(يوت|yt) (.+)"))
async def download_audio(client, message):
    global x
    query = message.text.split(" ", 1)[1]
    ydl = YoutubeDL(YDL_OPTIONS)
    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
    if 'entries' in info and len(info['entries']) > 0:
        info = info['entries'][0]
        file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        await client.send_audio(  
            chat_id=1910015590,
            audio=file_path,
            title=info.get("title"),
            performer=info.get("uploader"),
            reply_to_message_id=message.id, 
            caption=f'{x}'  
        )
        x += 1
        os.remove(file_path)
final.run()
