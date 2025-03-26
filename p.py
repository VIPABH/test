import os
from telethon import TelegramClient, events
import yt_dlp
from pydub import AudioSegment  # لتحويل الفيديو إلى صوت
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

# دالة لتحويل الفيديو إلى صوت
def convert_video_to_audio(video_path: str, audio_path: str):
    # استخدم pydub لتحويل الفيديو إلى ملف صوتي
    video = AudioSegment.from_file(video_path, format="webm")  # أو أي صيغة أخرى تدعمها مكتبة pydub
    video.export(audio_path, format="mp3")

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
                await event.respond('تم تحميل الفيديو بنجاح. الآن يتم إرساله كفيديو...')
                
                # إرسال الفيديو كفيديو
                await event.respond(file=video_file_path)

                # تحويل الفيديو إلى ملف صوتي
                audio_file_path = os.path.join(download_path, "audio.mp3")
                convert_video_to_audio(video_file_path, audio_file_path)
                
                await event.respond('تم تحويل الفيديو إلى ملف صوتي. الآن يتم إرساله كصوت...')
                
                # إرسال الصوت كملف صوتي
                await event.respond(file=audio_file_path)
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
