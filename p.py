import os
import json
import asyncio
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events
from yt_dlp import YoutubeDL

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not os.path.exists("downloads"):
    os.makedirs("downloads")

DATA_FILE = "downloaded_files.json"

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

def load_downloaded():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)  # قائمة بأسماء الملفات

def save_downloaded(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

ABH = TelegramClient("x", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

x = 1

@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def download_audio(event):
    global x
    query = event.pattern_match.group(2).strip()
    downloaded_files = load_downloaded()

    # محاولة إيجاد ملف مطابق في المجلد (بناءً على اسم الملف المتوقع)
    # لنستخدم YoutubeDL فقط لاستخراج معلومات بدون تحميل لتوقع اسم الملف
    ydl = YoutubeDL({**YDL_OPTIONS, 'noplaylist': True, 'quiet': True, 'skip_download': True})
    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=False)
    if 'entries' in info and len(info['entries']) > 0:
        info = info['entries'][0]
        expected_file = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        # إذا الملف موجود ضمن المخزن وفي التخزين الفعلي، أرسله مباشرة
        if expected_file in downloaded_files and os.path.exists(expected_file):
            await ABH.send_file(
                1910015590,
                file=expected_file,
                caption=f"{x}",
                attributes=[
                    DocumentAttributeAudio(
                        duration=info.get("duration", 0),
                        title=info.get('title'),
                        performer='ANYMOUS'
                    )
                ]
            )
            x += 1
            return

        # إذا لم يكن موجوداً، نحمّل الملف ثم نرسله
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
        if 'entries' in info:
            info = info['entries'][0]
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
        x += 1

        # أضف اسم الملف إلى القائمة ثم احفظها في JSON
        downloaded_files.append(file_path)
        save_downloaded(downloaded_files)

        os.remove(file_path)

ABH.run_until_disconnected()
