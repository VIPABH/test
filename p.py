import os
import asyncio
import shutil
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# --- وظيفة مساعدة لتثبيت المكتبات ---
def install_library(library_name):
    try:
        __import__(library_name)
        print(f"✅ مكتبة {library_name} مثبتة.")
        return True
    except ImportError:
        print(f"🔄 جاري تثبيت مكتبة {library_name}...")
        os.system(f"pip install {library_name}")
        try:
            __import__(library_name)
            print(f"✅ تم تثبيت مكتبة {library_name} بنجاح.")
            return True
        except ImportError:
            print(f"❌ فشل تثبيت مكتبة {library_name}. يرجى المحاولة مرة أخرى.")
            return False

# --- التحقق من TgCrypto ---
print("ℹ️ التحقق من مكتبة TgCrypto لتسريع Pyrogram...")
if not install_library("telethon"):
    print("⚠️ لم يتم تثبيت TgCrypto. قد يكون Pyrogram أبطأ. للمزيد: https://docs.pyrogram.org/topics/speedups")

# --- تثبيت Pyrogram ---
if install_library("pyrogram"):
    from pyrogram import Client, filters
else:
    exit()

# --- تثبيت yt-dlp --
if install_library("yt_dlp"):
    from yt_dlp import YoutubeDL
else:
    exit()

# --- وظيفة مساعدة للتحقق من ffmpeg ---
def check_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        print("✅ تم العثور على ffmpeg و ffprobe.")
        return True
    else:
        print("⚠️ لم يتم العثور على ffmpeg أو ffprobe.")
        print("   يرجى تثبيتهما لكي يتمكن البوت من تحويل الصوت إلى MP3.")
        print("   يمكنك تثبيتهما باستخدام:")
        print("   - على Linux (Debian/Ubuntu): sudo apt update && sudo apt install ffmpeg")
        print("   - على Linux (Fedora/CentOS): sudo dnf install ffmpeg")
        print("   - على macOS: brew install ffmpeg")
        print("   - على Windows: يمكنك تنزيلهما من موقع ffmpeg وإضافتهما إلى PATH.")
        print("   للمزيد: https://github.com/yt-dlp/yt-dlp#dependencies")
        return False

# --- التحقق من ffmpeg ---
if not check_ffmpeg():
    exit()

# --- إعدادات البوت | بس حط توكن ---
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')


# --- إعدادات التحميل بجودة متوسطة وتسريع الإرسال ---
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

@final.on_message(filters.regex(r"^يوت (.+)"))
async def download_audio(client, message):
    query = message.text.split(" ", 1)[1]
    wait_message = await message.reply("⏳ جاري البحث عن وتحميل الصوت... 🎧")

    ydl = YoutubeDL(YDL_OPTIONS)
    try:
        info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            await client.send_audio(  
                chat_id=message.chat.id,
                audio=file_path,
                title=info.get("title"),
                performer=info.get("uploader"),
                reply_to_message_id=message.id  
            )
            await wait_message.delete()
            os.remove(file_path)
        else:
            await wait_message.edit("🚫 لم يتم العثور على نتائج للبحث.")
    except Exception as e:
        await wait_message.edit(f"🚫 حدث خطأ أثناء التحميل:\n{e}")
    finally:
        pass

final.run()
