import os
from telethon import TelegramClient, events
import yt_dlp

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
client = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

# تأكد من أن مجلد التحميل موجود
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# دالة لتحميل الفيديو باستخدام yt-dlp
def download_video(video_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # لتحميل أفضل فيديو وصوت
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # تحديد اسم مجلد التحميل
        'noplaylist': True,  # لتجنب تحميل قوائم التشغيل
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_file = ydl.prepare_filename(info)
        return video_file  # إرجاع اسم الملف الذي تم تحميله

# التعامل مع الرسائل الواردة
@client.on(events.NewMessage(pattern='/فيديو'))
async def video_handler(event):
    try:
        video_url = event.text.split(None, 1)[1]  # استخراج الرابط المرسل من الرسالة
    except IndexError:
        await event.reply("يرجى إرسال رابط فيديو مع الأمر.")
        return
    
    try:
        # تحميل الفيديو
        video_file = download_video(video_url)
        # إرسال الفيديو إلى المستخدم
        await event.reply(file=video_file)
        # حذف الملف بعد إرساله لتوفير المساحة
        os.remove(video_file)
    except Exception as e:
        await event.reply(f'حدث خطأ أثناء تحميل الفيديو: {str(e)}')

# تشغيل البوت
if __name__ == "__main__":
    client.run_until_disconnected()
