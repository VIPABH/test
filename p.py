import os
import yt_dlp
from telethon import TelegramClient, events
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(url):
    file = "audio.mp3"
    opts = {'format': 'bestaudio', 'outtmpl': file, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]}
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    
    return file if os.path.exists(file) else None

@client.on(events.NewMessage(pattern='/تحميل'))
async def handler(event):
    msg = event.message.text.split(' ', 1)
    if len(msg) < 2:
        return await event.respond('ارسل رابط يوتيوب بعد /تحميل')

    await event.respond('جارٍ التحميل...')
    audio = await download_audio(msg[1])
    
    if audio:
        await event.client.send_file(event.chat_id, audio)
        os.remove(audio)
    else:
        await event.respond('فشل تحميل الصوت.')

client.run_until_disconnected()
