import logging
import os
import requests
import re
import telebot
from mutagen.mp3 import MP3
from telebot import types

# إعدادات البوت
bot_token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(bot_token)

# إعداد السجل
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

@bot.message_handler(commands=['start'])
def start(message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    welcome_message = f"مرحبًا {username}!\n\nأرسل رابط فيديو يوتيوب لتحميل الصوت كملف موسيقي قابل للسماع."
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    msg = message.text.strip()
    found_links = find_urls(msg)

    if not found_links:
        bot.reply_to(message, "❗ الرجاء إرسال رابط يوتيوب صحيح.")
        return

    youtube_url = found_links[0]

    if 'youtu.be/' in youtube_url:
        video_id = youtube_url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/watch?v=' in youtube_url:
        video_id = youtube_url.split('v=')[1].split('&')[0]
    else:
        bot.reply_to(message, "❗ الرابط غير مدعوم.")
        return

    audio_api_url = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

    try:
        audio_response = requests.get(audio_api_url, timeout=60)
        audio_response.raise_for_status()
    except Exception as e:
        logging.error(f"Download Audio Error: {str(e)}")
        bot.reply_to(message, "❌ تعذر تحميل الملف الصوتي من السيرفر.")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    temp_file_path = f"downloads/{video_id}.mp3"
    with open(temp_file_path, 'wb') as f:
        f.write(audio_response.content)

    # التحقق من حجم الملف
    if os.path.getsize(temp_file_path) > 80 * 1024 * 1024:
        os.remove(temp_file_path)
        bot.reply_to(message, "⚠️ الملف الصوتي أكبر من 40 ميغابايت، لا يمكن إرساله.")
        return

    # استخراج مدة الصوت
    try:
        audio_file = MP3(temp_file_path)
        duration = int(audio_file.info.length)
    except Exception as e:
        duration = 0  # إذا فشل في القراءة نخليه صفر
        logging.error(f"MP3 Duration Error: {str(e)}")

    # إرسال الملف كـ Audio رسمي
    with open(temp_file_path, 'rb') as audio:
        bot.send_audio(
            chat_id=message.chat.id,
            audio=audio,
            caption="🎵 تم التحميل بنجاح.",
            title="موسيقى من يوتيوب",    # هنا الاسم يظهر
            performer="YouTube",          # هنا المؤدي يظهر
            duration=duration              # المدة تظهر
        )

    os.remove(temp_file_path)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

print("✅ جاري تشغيل البوت...")
bot.polling(non_stop=True)
