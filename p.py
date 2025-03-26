import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv
import io
import requests

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إعدادات العميل
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لتحميل الفيديو باستخدام yt-dlp إلى الذاكرة
async def download_video_to_memory(url: str):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extractaudio': False,  # لا يتم استخراج الصوت فقط
        'noplaylist': True,  # تحميل فيديو واحد فقط
        'outtmpl': '-',  # إخراج الفيديو إلى المعيار (من غير حفظه في ملف)
    }

    # تحميل الفيديو في الذاكرة باستخدام yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)

        # العثور على أول صيغة فيديو صالحة
        video_url = result['formats'][0]['url']
        
        # تحميل البيانات من الفيديو باستخدام requests
        video_data = requests.get(video_url).content
        return video_data

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    try:
        # استخدم الرابط المرسل لتحميل الفيديو
        url = event.message.text.split(' ', 1)[1]
        
        await event.respond('جارٍ تحميل الفيديو...')
        
        # تحميل الفيديو إلى الذاكرة
        video_data = await download_video_to_memory(url)
        
        # إرسال الفيديو مباشرة من الذاكرة
        await event.respond(file=io.BytesIO(video_data), force_document=False)

    except IndexError:
        await event.respond('الرجاء إرسال رابط الفيديو بعد الأمر /download')
    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

# تشغيل البوت
client.start()
client.run_until_disconnected()
