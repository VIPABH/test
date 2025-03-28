import os
from telethon.tl.custom import Button
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
load_dotenv()
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
async def download_audio(query: str):
    ydl_opts = {
        'format': 'worstaudio',
        'quiet': False,
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
            'nopostoverwrites': True,
        }],
        'noprogress': True,
        'default_search': 'ytsearch',
    }
    if not query.startswith(("http://", "https://")):
        query = f"ytsearch1:{query}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            output_file = ydl.prepare_filename(info)
            audio_file = output_file.rsplit('.', 1)[0] + ".mp3"
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            raise FileNotFoundError("⚠️ فشل تحميل الملف الصوتي!")
        return audio_file
    except Exception as e:
        with open("log.txt", "a") as log_file:
            log_file.write(f"خطأ: {e}\n")
        return None
@client.on(events.NewMessage(pattern='تحميل'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('ارسل الرابط أو النص المطلوب للبحث عن الصوت.')
            return
        query = msg_parts[1]
        if "http" in query:
            await event.respond('جارٍ التحميل من الرابط...')
            audio_file = await download_audio(query)
        else:
            await event.respond('جارٍ البحث عن الصوت...')
            audio_file = await download_audio(query)
        if audio_file:
            button = [Button.url("chanel", "https://t.me/sszxl")]
            await event.client.send_file(
                event.chat_id, 
                audio_file, 
                caption='[**Enjoy dear**](https://t.me/VIPABH_BOT)',
                buttons=button,
                reply_to=event.message.id
            )
            os.remove(audio_file)
        else:
            await event.respond("فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")
    except Exception as e:
        await event.respond(f'خطأ: {e}')
client.run_until_disconnected()
