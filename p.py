from telethon import TelegramClient, events
import yt_dlp
import os

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
client = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)


# دالة لتنزيل الفيديو
def download_video(url):
    ydl_opts = {
        'format': '229',  # اختر الجودة المناسبة، هنا اخترت 229
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # حفظ الفيديو في مجلد downloads
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@client.on(events.NewMessage(pattern='/download'))
async def download_handler(event):
    url = event.text.split(' ')[1]  # الحصول على رابط الفيديو بعد /download
    await event.reply('جاري تنزيل الفيديو...')
    
    # تنزيل الفيديو باستخدام yt-dlp
    download_video(url)
    
    # إرسال الفيديو المحمل إلى المستخدم
    video_path = 'downloads/' + url.split('/')[-1] + '.mp4'  # مسار الفيديو المحمل
    if os.path.exists(video_path):
        await event.reply(file=video_path)
    else:
        await event.reply('حدث خطأ أثناء تحميل الفيديو.')

client.run_until_disconnected()
