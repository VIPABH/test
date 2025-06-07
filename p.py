import os
import asyncio
import json
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events, Button
from yt_dlp import YoutubeDL
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ABH = TelegramClient("x", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)
if not os.path.exists("downloads"):
    os.makedirs("downloads")
CACHE_FILE = "audio_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        audio_cache = json.load(f)
else:
    audio_cache = {}
def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(audio_cache, f, ensure_ascii=False, indent=2)
YDL_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'cookiefile': "cookies.txt",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}
@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def download_audio(event):
    try:
        query = event.pattern_match.group(2)
        b = Button.url('CHANNEL', 'https://t.me/X04OU')
        for val in audio_cache.values():
            if isinstance(val, dict) and val.get("query") == query:
                await ABH.send_file(
                    1910015590,
                    file=val["file_id"],
                    caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)",
                    attributes=[
                        DocumentAttributeAudio(
                            duration=val.get("duration", 0),
                            title=val.get("title"),
                            performer='ANYMOUS'
                        )
                    ],
                    buttons=[b]
                )
                return  
        ydl = YoutubeDL(YDL_OPTIONS)
        search_result = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=False)
        if 'entries' not in search_result or not search_result['entries']:
            await event.reply("لم يتم العثور على نتائج.")
            return
        video_info = search_result['entries'][0]
        video_id = video_info.get('id')
        if video_id in audio_cache:
            val = audio_cache[video_id]
            await ABH.send_file(
                1910015590,
                file=val["file_id"],
                caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)",
                attributes=[
                    DocumentAttributeAudio(
                        duration=val.get("duration", 0),
                        title=val.get("title"),
                        performer='ANYMOUS'
                    )
                ],
                buttons=[b]
            )
            return
        download_info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
        downloaded_video = download_info['entries'][0]
        file_path = ydl.prepare_filename(downloaded_video).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        msg = await ABH.send_file(
            1910015590,
            file=file_path,
            caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)",
            attributes=[
                DocumentAttributeAudio(
                    duration=downloaded_video.get("duration", 0),
                    title=downloaded_video.get("title"),
                    performer='ANYMOUS'
                )
            ],
            buttons=[b]
        )
        audio_cache[downloaded_video.get("id")] = {
            "file_id": msg.file.id,
            "title": downloaded_video.get("title"),
            "duration": downloaded_video.get("duration", 0),
            "query": query
        }
        save_cache()
    except Exception as e:
        await ABH.send_message(1910015590, f"Error: {str(e)}")
ABH.run_until_disconnected()
