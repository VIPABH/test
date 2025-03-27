import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
import io

# تحميل المتغيرات البيئية
load_dotenv()

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# التحقق من صحة القيم البيئية
if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى التأكد من ضبط API_ID, API_HASH، و BOT_TOKEN في ملف .env")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لتحميل الصوت
async def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # دعم الفيديوهات المحمية إذا لزم الأمر
        'outtmpl': '-',  # إخراج الملف إلى الذاكرة
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    buffer = io.BytesIO()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info = ydl.extract_info(url, download=False)
        audio_title = info.get('title', 'audio')  # استخدم العنوان الافتراضي عند الحاجة

    buffer.seek(0)
    return buffer, f"{audio_title}.mp3"

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('الرجاء إرسال رابط الفيديو بعد الأمر /download')
            return
        
        url = msg_parts[1]
        await event.respond('جارٍ تحميل الصوت...')

        # تحميل الصوت إلى الذاكرة
        audio_data, filename = await download_audio(url)

        # إرسال الصوت
        await event.respond(file=audio_data, force_document=False, voice=True, attributes={'filename': filename})

    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

client.run_until_disconnected()
