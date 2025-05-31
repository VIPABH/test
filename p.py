from telethon import events
from telethon.sync import TelegramClient
import os
import subprocess
from dotenv import load_dotenv
import uuid

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = TelegramClient("spotify_bot", api_id, api_hash).start(bot_token=bot_token)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@bot.on(events.NewMessage(pattern=r'^\.سبوت (.+)'))
async def handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جاري معالجة الطلب: {query}")
    
    filename = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOADS_DIR, f"{filename}.mp3")

    try:
        # المرحلة 1: جرب spotdl
        result = subprocess.run(
            ["spotdl", query, "--output", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if os.path.exists(output_path):
            await bot.send_file(event.chat_id, file=output_path, reply_to=event.id)
            os.remove(output_path)
            return
        else:
            raise Exception("❌ spotdl فشل، سنجرب YouTube...")

    except Exception as e:
        await event.reply(str(e))

    # المرحلة 2: استخدم yt-dlp من YouTube
    try:
        yt_output = os.path.join(DOWNLOADS_DIR, f"{filename}.%(ext)s")
        result = subprocess.run(
            ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o", yt_output, f"ytsearch:{query}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # التحقق من وجود الملف الذي تم تحميله
        downloaded_file = None
        for f in os.listdir(DOWNLOADS_DIR):
            if filename in f and f.endswith(".mp3"):
                downloaded_file = os.path.join(DOWNLOADS_DIR, f)
                break

        if downloaded_file:
            await bot.send_file(event.chat_id, file=downloaded_file, reply_to=event.id)
            os.remove(downloaded_file)
        else:
            await event.reply("⚠️ فشل تحميل الصوت من YouTube أيضاً.")

    except Exception as e:
        await event.reply(f"⚠️ خطأ في yt-dlp: {str(e)}")

print("🤖 بوت التحميل الصوتي جاهز...")
bot.run_until_disconnected()
