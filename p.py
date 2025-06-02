import os
import asyncio
import json
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events
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
    # 'cookiefile': "cookies.txt",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}
x = 1
@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def download_audio(event):
    global x
    try:
        query = event.pattern_match.group(2)
        ydl = YoutubeDL(YDL_OPTIONS)
        for key, val in audio_cache.items():
            if isinstance(val, dict) and val.get("query") == query:
                await ABH.send_file(
                    1910015590,
                    file=val["file_id"],
                    caption=f"{x}",
                    attributes=[
                        DocumentAttributeAudio(
                            duration=val.get("duration", 0),
                            title=val.get("title"),
                            performer='ANYMOUS'
                        )
                    ]
                )
                x += 1
                return
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=False)
        if 'entries' in info and len(info['entries']) > 0:
            video_info = info['entries'][0]
            video_id = video_info.get('id')
            if video_id in audio_cache:
                val = audio_cache[video_id]
                if isinstance(val, dict):
                    await ABH.send_file(
                        1910015590,
                        file=val["file_id"],
                        caption=f"{x}",
                        attributes=[
                            DocumentAttributeAudio(
                                duration=val.get("duration", 0),
                                title=val.get("title"),
                                performer='ANYMOUS'
                            )
                        ]
                    )
                    x += 1
                    return
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            msg = await ABH.send_file(
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
            audio_cache[info.get("id")] = {
                "file_id": msg.file.id,
                "title": info.get("title"),
                "duration": info.get("duration", 0),
                "query": query
            }
            save_cache()
            x += 1
    except Exception as e:
        await ABH.send_message(
            1910015590,
            e
        )
ABH.run_until_disconnected()
