import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
import io

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إعدادات العميل
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لتحميل الفيديو باستخدام yt-dlp
async def download_video(url: str):
    ydl_opts = {
        'outtmpl': '-',  # تحميل الفيديو مباشرة إلى الذاكرة
        'quiet': True,
        'cookiefile': 'cookies.txt',  # استخدام ملف الكوكيز لدعم الفيديوهات المحمية
        'format': 'bestvideo+bestaudio/best',  # اختيار أفضل فيديو وصوت متاحين
        'noplaylist': True,  # لتجنب تحميل قوائم التشغيل
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        video_url = result['formats'][0]['url']
        video_data = yt_dlp.request.urlopen(video_url).read()
        return video_data

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    try:
        # استخدم الرابط المرسل لتحميل الفيديو
        url = event.message.text.split(' ', 1)[1]
        
        await event.respond('جارٍ تحميل الفيديو...')

        # تحميل الفيديو إلى الذاكرة
        video_data = await download_video(url)
        
        # إرسال الفيديو مباشرة من الذاكرة
        await event.respond(file=io.BytesIO(video_data), force_document=False)

    except IndexError:
        await event.respond('الرجاء إرسال رابط الفيديو بعد الأمر /download')
    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

# تشغيل البوت
client.start()
client.run_until_disconnected()
