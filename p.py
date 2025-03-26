
from telethon import TelegramClient, events
import yt_dlp as youtube_dl
# جلب بيانات API من المتغيرات البيئية
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
# إعدادات العميل
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# دالة لتحميل الفيديو باستخدام yt-dlp
async def download_video(url: str, download_path: str):
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'quiet': True,
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# الحدث عند تلقي رسالة
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    # استخدم الرابط المرسل لتحميل الفيديو
    url = event.message.text.split(' ', 1)[1]
    
    # تحديد المسار لحفظ الفيديو
    download_path = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_path, exist_ok=True)
    
    await event.respond('جارٍ تحميل الفيديو...')
    
    try:
        # تحميل الفيديو
        await download_video(url, download_path)
        await event.respond(f'تم تحميل الفيديو بنجاح: {url}')
    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

# تشغيل البوت
client.start()
client.run_until_disconnected()
