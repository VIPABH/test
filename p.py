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
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'quiet': True,
        'cookiefile': 'cookies.txt'  # استخدام ملف الكوكيز لدعم الفيديوهات المحمية
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    try:
        # استخدم الرابط المرسل لتحميل الفيديو
        url = event.message.text.split(' ', 1)[1]
        
        # تحديد المسار لحفظ الفيديو
        download_path = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_path, exist_ok=True)
        
        await event.respond('جارٍ تحميل الفيديو...')
        
        # تحميل الفيديو
        await download_video(url, download_path)
        
        # البحث عن الملفات في المجلد بعد التحميل
        downloaded_files = [f for f in os.listdir(download_path) if f.endswith(('.webm', '.mp4'))]
        
        if downloaded_files:
            # اختيار أول ملف تم تحميله
            video_file_path = os.path.join(download_path, downloaded_files[0])
            
            # تحقق من وجود الملف قبل إرساله
            if os.path.exists(video_file_path):
                await event.respond('تم تحميل الفيديو بنجاح. الآن يتم إرساله...')
                # إرسال الفيديو باستخدام `file=`
                await event.respond(file=video_file_path, caption="هنا هو الفيديو الذي طلبته!")
            else:
                await event.respond('حدث خطأ: الفيديو غير موجود في المسار المحدد.')
        else:
            await event.respond('لم يتم العثور على فيديو في المجلد.')

    except IndexError:
        await event.respond('الرجاء إرسال رابط الفيديو بعد الأمر /download')
    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

# تشغيل البوت
client.start()
client.run_until_disconnected()
