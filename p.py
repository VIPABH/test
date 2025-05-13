import os
import re
import asyncio
from yt_dlp import YoutubeDL
from telethon import TelegramClient, events

# إعداد القيم من البيئة
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

# إنشاء مجلد التنزيل إن لم يكن موجوداً
os.makedirs("downloads", exist_ok=True)

# إعداد البوت
ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# خيارات التحميل
YDL_OPTIONS = {
    'format': 'bestaudio/best[abr<=160]',
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

# تنظيف أسماء الملفات من الرموز غير المدعومة
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@ABH.on(events.NewMessage(pattern='يوت|yt'))
async def download_audio(event):
    try:
        query = event.text.split(" ", 1)[1]
    except IndexError:
        await event.reply("❗️يرجى كتابة اسم الأغنية بعد الأمر.")
        return

    try:
        ydl = YoutubeDL(YDL_OPTIONS)
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
            title = sanitize_filename(info.get("title", "audio"))
            file_path = f"downloads/{title}.mp3"

            await ABH.send_file(
                event.chat_id,
                file=file_path,
                voice=False,
                caption=info.get("title", ""),
                reply_to=event.id
            )

            os.remove(file_path)
        else:
            await event.reply("🚫 لم يتم العثور على نتائج للبحث.")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء التحميل:\n`{str(e)}`")

ABH.run_until_disconnected()
