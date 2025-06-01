import os
import asyncio
from yt_dlp import YoutubeDL
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAudio
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
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}

bot = TelegramClient('youtubeaudio_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("مرحباً! أرسل:\n\nيوت + اسم الأغنية")

@bot.on(events.NewMessage(pattern=r"^(يوت|yt) (.+)"))
async def download_audio(event):
    query = event.pattern_match.group(2)
    sender = await event.get_sender()
    chat_id = event.chat_id

    await event.reply("⏳ يتم البحث وتحميل الصوت...")

    try:
        # تحميل وتحويل الصوت في خيط منفصل
        def process_audio():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                file_path = ydl.prepare_filename(info)
                if file_path.endswith('.webm') or file_path.endswith('.m4a'):
                    file_path = file_path.rsplit('.', 1)[0] + '.mp3'
                return file_path, info

        file_path, info = await asyncio.to_thread(process_audio)

        # تحقق من وجود الملف وعدم كونه فارغ
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            await event.reply("❌ فشل في التحميل. الملف غير صالح أو فارغ.")
            return

        # إرسال الملف كـ mp3
        await bot.send_file(
            chat_id=chat_id,
            file=file_path,
            caption=f"🎵 {info.get('title')}",
            attributes=[
                DocumentAttributeAudio(
                    duration=info.get("duration"),
                    title=info.get("title"),
                    performer=info.get("uploader")
                )
            ],
            reply_to=event.id
        )

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء التحميل:\n{str(e)}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

print("🤖 البوت يعمل الآن.")
bot.run_until_disconnected()
