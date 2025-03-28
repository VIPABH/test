import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
api_id, api_hash, bot_token = os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(query: str):
    opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)
            output_file = ydl.prepare_filename(info)
            print("تم التحميل:", output_file)  # طباعة المسار للتأكد
            return output_file if os.path.exists(output_file) else None
        except Exception as e:
            print("خطأ:", e)
            return None

@client.on(events.NewMessage(pattern='يوت'))
async def audio_handler(event):
    query = event.text.split(' ', 1)[1] if ' ' in event.text else None
    if not query:
        return await event.respond("أرسل الرابط أو اسم الفيديو.")
    
    audio_file = await download_audio(query)
    if audio_file:
        await event.respond("جاري الإرسال...")
        await event.client.send_file(event.chat_id, audio_file)
        os.remove(audio_file)
    else:
        await event.respond("فشل التحميل، جرب رابط آخر.")

client.run_until_disconnected()
