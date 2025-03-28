import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
api_id, api_hash, bot_token = os.getenv('API_ID'), os.getenv('API_HASH'), os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(query: str):
    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"  # استخدام ytsearch عند البحث النصي

    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    
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
    msg_parts = event.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond("أرسل الرابط أو اسم الفيديو.")
    
    query = msg_parts[1]
    audio_file = await download_audio(query)
    
    if audio_file:
        await event.respond("جاري الإرسال...")
        await event.client.send_file(event.chat_id, audio_file)
        os.remove(audio_file)
    else:
        await event.respond("فشل التحميل، جرب رابط آخر أو تحقق من الاتصال.")

client.run_until_disconnected()
