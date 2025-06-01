import os
import re
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

# ملف json لحفظ أسماء الملفات المُرسلة
CACHE_FILE = "sent_files.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        sent_files = json.load(f)
else:
    sent_files = {}

def safe_filename(filename: str) -> str:
    # تنظيف الاسم من الأحرف غير المسموح بها في أسماء الملفات
    return re.sub(r'[\\/*?:"<>|#]', "_", filename)

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

@ABH.on(events.NewMessage(pattern=r'^(يوت|yt) (.+)'))
async def download_audio(event):
    query = event.pattern_match.group(2)

    try:
        ydl = YoutubeDL(YDL_OPTIONS)
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=False)

        if 'entries' not in info or len(info['entries']) == 0:
            return  # لا يوجد نتائج

        info = info['entries'][0]
        # جلب اسم الملف المتوقع وتنظيفه
        file_name = ydl.prepare_filename(info)
        file_name = file_name.replace(".webm", ".mp3").replace(".m4a", ".mp3")
        file_name = safe_filename(file_name)

        # إذا الملف موجود في الـ cache أرسله بدون تحميل جديد
        if file_name in sent_files:
            if os.path.exists(file_name):
                await ABH.send_file(
                    event.chat_id,
                    file=file_name,
                    caption=info.get('title', ''),
                    attributes=[
                        DocumentAttributeAudio(
                            duration=info.get("duration", 0),
                            title=info.get('title'),
                            performer='ANYMOUS'
                        )
                    ],
                    reply_to=event.id
                )
                return
            else:
                # الملف غير موجود فعلياً رغم وجوده في القائمه، نزيله
                sent_files.pop(file_name)
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(sent_files, f, ensure_ascii=False, indent=2)

        # تحميل الملف فعليًا
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)

        
        await ABH.send_file(
            event.chat_id,
            file=file_name,
            caption=info.get('title', ''),
            attributes=[
                DocumentAttributeAudio(
                    duration=info.get("duration", 0),
                    title=info.get('title'),
                    performer='ANYMOUS'
                )
            ],
        )

        # حفظ الملف في القائمه لتفادي إعادة التحميل
        sent_files[file_name] = True
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(sent_files, f, ensure_ascii=False, indent=2)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء التحميل أو الإرسال:\n{str(e)}")

ABH.run_until_disconnected()
