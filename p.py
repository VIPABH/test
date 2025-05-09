import os
import asyncio
import shutil
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not os.path.exists("downloads"):
    os.makedirs("downloads")

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

final = Client("youtube_audio_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@final.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("مرحباً! أرسل:\n\nيوت + اسم الأغنية")

@final.on_message(filters.regex(r"^(يوت|yt) (.+)"))
async def download_audio(client, message):
    query = message.text.split(" ", 1)[1]
    # wait_message = await message.reply("⏳ جاري البحث عن وتحميل الصوت... 🎧")
    x = 0
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
            reply_to_message_id=message.id  
        )
        x += 1
        await client.send_message(
            chat_id=message.chat.id,
            text=str(x),
            protect_content=True  # تمنع التحويل والنسخ
    )        # await wait_message.delete()
        os.remove(file_path)
    # else:
        # await wait_message.edit("🚫 لم يتم العثور على نتائج للبحث.")
# except Exception as e:
    # await wait_message.edit(f"🚫 حدث خطأ أثناء التحميل:\n{e}")
# finally:
    # pass

final.run()
