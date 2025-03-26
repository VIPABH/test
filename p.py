import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

# إعدادات العميل
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لتحميل الفيديو باستخدام yt-dlp مع دعم الكوكيز
async def download_video(url: str, download_path: str):
    # التأكد من أن ملف الكوكيز موجود
    if not os.path.exists("cookies.txt"):
        raise FileNotFoundError("ملف cookies.txt غير موجود، تأكد من استخراجه بشكل صحيح!")

    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'quiet': False,  # تعطيل الوضع الصامت لرؤية الأخطاء عند الحاجة
        'cookiefile': 'cookies.txt'  # استخدام ملف الكوكيز لدعم الفيديوهات المحمية
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise RuntimeError(f"فشل تحميل الفيديو: {str(e)}")

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern=r'^/download\s+(.+)$'))
async def handler(event):
    try:
        # استخراج الرابط من الرسالة
        url = event.pattern_match.group(1)

        # تحديد المسار لحفظ الفيديو
        download_path = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_path, exist_ok=True)

        await event.respond('جارٍ تحميل الفيديو...')

        # تحميل الفيديو
        await download_video(url, download_path)
        await event.respond(f'تم تحميل الفيديو بنجاح: {url}')
    except FileNotFoundError as e:
        await event.respond(f"خطأ: {str(e)}\nيرجى التأكد من استخراج الكوكيز بشكل صحيح.")
    except RuntimeError as e:
        await event.respond(f"خطأ أثناء التحميل: {str(e)}")
    except Exception as e:
        await event.respond(f'حدث خطأ غير متوقع: {str(e)}')

# تشغيل البوت
client.run_until_disconnected()
