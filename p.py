
from pyrogram import Client, filters
import yt_dlp
import os

# توكن البوت الذي تحصل عليه من BotFather
bot_token = os.getenv('BOT_TOKEN')

# إعداد البوت باستخدام Pyrogram
app = Client("my_bot", bot_token=bot_token)

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
@app.on_message(filters.command("فيديو"))
async def video_handler(client, message):
    video_url = message.text.split(None, 1)[1]  # استخراج الرابط المرسل من الرسالة
    try:
        # تحميل الفيديو
        video_file = download_video(video_url)
        # إرسال الفيديو إلى المستخدم
        await message.reply_video(video_file)
        # حذف الملف بعد إرساله لتوفير المساحة
        os.remove(video_file)
    except Exception as e:
        await message.reply(f'حدث خطأ أثناء تحميل الفيديو: {str(e)}')

# تشغيل البوت
if __name__ == "__main__":
    app.run()
