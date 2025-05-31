import os
import subprocess
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = TelegramClient("spotify_bot", api_id, api_hash).start(bot_token=bot_token)

# المسار الذي سيتم فيه حفظ ملفات MP3
DOWNLOAD_DIR = "spotify_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_spotify_audio(spotify_url):
    try:
        result = subprocess.run(
            ["spotdl", spotify_url, "--output", f"{DOWNLOAD_DIR}/"],
            capture_output=True, text=True
        )
        print(result.stdout)
        
        # البحث عن ملف MP3 داخل المجلد
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith(".mp3"):
                return os.path.join(DOWNLOAD_DIR, file)
    except Exception as e:
        print(f"❌ خطأ أثناء التنزيل: {e}")
        return None

@bot.on(events.NewMessage(pattern=r'^/spotify (.+)'))
async def handler(event):
    url = event.pattern_match.group(1).strip()
    
    await event.reply("🔄 جاري تحميل الصوت من Spotify...")

    audio_path = download_spotify_audio(url)
    if not audio_path:
        await event.reply("❌ فشل التنزيل. تأكد من أن الرابط صحيح.")
        return

    try:
        await bot.send_file(event.chat_id, file=audio_path, reply_to=event.id)
        await event.reply("✅ تم الإرسال بنجاح.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء الإرسال: {e}")
    finally:
        os.remove(audio_path)

print("🤖 بوت Spotify يعمل...")
bot.run_until_disconnected()
