import os
from telethon.tl.custom import Button
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
import asyncio

load_dotenv()
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',  # تحميل أفضل جودة صوتية
        'quiet': True,               # إخفاء معظم الرسائل
        'noplaylist': True,          # عدم تحميل قوائم التشغيل
        'cookiefile': 'cookies.txt', # استخدام الكوكيز إذا كانت مطلوبة
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # تحويل الملف الصوتي
            'preferredcodec': 'mp3',
            'preferredquality': '64',
            'nopostoverwrites': True,  # تجنب الكتابة فوق الملفات القديمة
        }],
        'noprogress': True,           # إخفاء شريط التقدم
        'default_search': 'ytsearch', # البحث في يوتيوب
        'extractaudio': True,         # استخراج الصوت فقط
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            output_file = ydl.prepare_filename(info)
            audio_file = output_file.rsplit('.', 1)[0] + ".mp3"

        if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            return audio_file
    except Exception:
        return None

@client.on(events.NewMessage(pattern='تحميل'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            return await event.respond('ارسل الرابط أو النص المطلوب.')
        
        query = msg_parts[1]
        audio_file = await download_audio(query)

        if audio_file:
            button = [Button.url("chanel", "https://t.me/sszxl")]
            await event.client.send_file(event.chat_id, audio_file, caption='[**Enjoy dear**](https://t.me/VIPABH_BOT)', buttons=button, reply_to=event.message.id)
            os.remove(audio_file)
        else:
            await event.respond("فشل تحميل الصوت.")
    except Exception as e:
        await event.respond(f'خطأ: {e}')

client.run_until_disconnected()
