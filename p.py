import logging
import os
import requests
import re
import telebot

bot_token = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(bot_token)

logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

@bot.message_handler(commands=['start'])
def start(message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    welcome_message = f"مرحبًا {username}!\nأرسل رابط يوتيوب فقط لتحميل الصوت."
    bot.send_message(message.chat.id, welcome_message)

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    msg = message.text.strip()

    found_links = find_urls(msg)
    if not found_links:
        bot.reply_to(message, "❗ الرجاء إرسال رابط يوتيوب فقط.")
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

    temp_file = f"downloads/{video_id}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(audio_response.content)

    if os.path.getsize(temp_file) > 80 * 1024 * 1024:
        os.remove(temp_file)
        bot.reply_to(message, "⚠️ الملف الصوتي أكبر من 40 ميغابايت، لا يمكن إرساله.")
        return

    audio = open(temp_file, 'rb')
    bot.send_audio(
        message.chat.id,
        audio,
        caption="🎵 تم التحميل بنجاح.",
        title="صوت من يوتيوب",
        performer="YouTube",
        duration=0
    )
    audio.close()

    os.remove(temp_file)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

print("جاري تشغيل البوت...")
bot.polling(non_stop=True)
