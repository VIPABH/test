import os
import asyncio
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
        'format': 'worstaudio',  # لتحميل أقل جودة صوتية
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
        'noprogress': True,
        'extractaudio': True,
        'default_search': 'ytsearch',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # تحويل الصوت إلى MP3
            'preferredquality': '64',  # ضغط الصوت لجودة أقل (أسرع)
            'nopostoverwrites': True,
        }],
    

        'progress_hooks': [lambda d: None],  # إخفاء التقدم بشكل كامل
        'concurrent_fragment_downloads': 10,  # زيادة عدد الأجزاء التي يتم تحميلها في نفس الوقت
        'max_filesize': 50 * 1024 * 1024,  # تحديد الحد الأقصى للحجم (50 ميجابايت)
        'socket_timeout': 30,  # تحديد مهلة الاتصال لتقليل التأخير
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        output_file = ydl.prepare_filename(info)
        audio_file = output_file.rsplit('.', 1)[0] + ".mp3"
        if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            return audio_file
@client.on(events.NewMessage(pattern='يوت'))
async def handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond('ارسل الرابط أو النص المطلوب.')
    query = msg_parts[1]
    audio_file = await download_audio(query)
    if audio_file:
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            audio_file, 
            caption='**[Enjoy dear]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(audio_file)
    else:
        await event.respond("فشل تحميل الصوت.")
client.run_until_disconnected()
