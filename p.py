import logging
import os
import requests
import time
import re
import telebot
from telebot import types

bot_token = 'token'

YOUTUBE_API_KEY = 'AIzaSyDLp3YbxDpGMGHmGS7Kx39GLqHmYJ5b8XE'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

bot = telebot.TeleBot(bot_token)

cooldown = {}
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')
@bot.message_handler(func=lambda message: message.text.lower().startswith(('يوت ', 'yt ')))
def yt_handler(message):
    msg = message.text.lower()
    query = msg.split(" ", 1)[1]

    params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'maxResults': 1,
        'type': 'video'
    }
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10).json()

    if 'items' not in r or len(r['items']) == 0:
        bot.reply_to(message, "ما لكيت شي لهالاسم.")
        return

    video_id = r['items'][0]['id']['videoId']
    title = r['items'][0]['snippet']['title']
    safe_title = sanitize_filename(title)[:50]

    audio_api = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"
    audio_data = requests.get(audio_api, timeout=15)
    if audio_data.status_code != 200:
        bot.reply_to(message, "للأسف، ما قدرت أنزل الصوت. يمكن السيرفر فيه مشكلة.")
        return
    temp_file = f"{safe_title}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(audio_data.content)

    if os.path.getsize(temp_file) > 40 * 1024 * 1024:
        os.remove(temp_file)
        bot.reply_to(message, "الملف أكبر من 40MB، ما أقدر أرسله.")
        return

    bot.send_audio(message.chat.id, open(temp_file, 'rb'))
    os.remove(temp_file)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

print("جاري تشغيل البوت...")
bot.polling(non_stop=True)
