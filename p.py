import os
from telethon import TelegramClient, events
import yt_dlp
from pydub import AudioSegment
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

# دالة لتحميل الفيديو باستخدام yt-dlp مع دعم الكوكيز
async def download_video(url: str):
    ydl_opts = {
        'outtmpl': '-',  # تحميل الفيديو مباشرة إلى الذاكرة
        'quiet': True,
        'cookiefile': 'cookies.txt',  # استخدام ملف الكوكيز لدعم الفيديوهات المحمية
        'format': 'bestvideo+bestaudio/best',  # اختيار أفضل فيديو وصوت متاحين
        'noplaylist': True,  # لتجنب تحميل قوائم التشغيل
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',  # تحويل الفيديو إلى صوت
            'preferredcodec': 'mp3',  # تحديد صيغة الملف الصوتي (mp3)
            'preferredquality': '192',  # جودة الصوت (192 kbps)
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        video_url = result['formats'][0]['url']
        video_data = yt_dlp.request.urlopen(video_url).read()
        return video_data

# دالة لتحويل الفيديو إلى صوت
def convert_video_to_audio(video_data: bytes):
    try:
        # تحويل الفيديو إلى ملف مؤقت في الذاكرة باستخدام BytesIO
        video = AudioSegment.from_file(io.BytesIO(video_data), format="mp4")  # تحديد التنسيق كـ mp4
        audio_io = io.BytesIO()
        video.export(audio_io, format="mp3")
        audio_io.seek(0)  # إعادة التوجيه إلى بداية الملف
        return audio_io
    except Exception as e:
        raise Exception(f"فشل تحويل الفيديو إلى صوت: {str(e)}")

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
        
        # تحويل الفيديو إلى ملف صوتي
        audio_io = convert_video_to_audio(video_data)
        await event.respond('تم تحويل الفيديو إلى ملف صوتي. الآن يتم إرساله كصوت...')
        
        # إرسال الصوت كملف صوتي
        await event.respond(file=audio_io)

    except IndexError:
        await event.respond('الرجاء إرسال رابط الفيديو بعد الأمر /download')
    except Exception as e:
        await event.respond(f'حدث خطأ أثناء التحميل: {str(e)}')

# تشغيل البوت
client.start()
client.run_until_disconnected()
