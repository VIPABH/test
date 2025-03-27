import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
import io

load_dotenv()

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': '-',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    buffer = io.BytesIO()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    buffer.seek(0)
    return buffer

@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('ارسل رابط الفيديو بعد /download')
            return
        url = msg_parts[1]
        await event.respond('جارٍ التحميل...')
        audio_data = await download_audio(url)
        await event.client.send_file(event.chat_id, audio_data, voice_note=True)
    except Exception as e:
        await event.respond(f'خطأ: {str(e)}')

client.run_until_disconnected()
