import logging
import os
import requests
import time
import re
import telebot
from telebot import types

BOT_TOKEN = 'BOT_TOKEN'

YOUTUBE_API_KEY = 'AIzaSyDLp3YbxDpGMGHmGS7Kx39GLqHmYJ5b8XE'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

bot = telebot.TeleBot(BOT_TOKEN)

cooldown = {}
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

@bot.message_handler(commands=['start'])
def start(message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    
    welcome_message = f"مرحبًا {username}!\nأنا بوت يوتيوب، أقدر أساعدك في تحميل أغاني من يوتيوب وإرسالها لك مباشرة هنا.\n\nكل ما عليك هو كتابة 'يوت' أو 'yt' متبوعًا باسم الأغنية، وراح أرسل لك الملف الصوتي.\n\nلا تنسى تضيفني إلى مجموعاتك وتستفيد من الخدمة في كل مكان!"
    
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("اضفني إلى مجموعاتك", url="https://t.me/YOUR_BOT_USERNAME")
    markup.add(button)
    
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower().startswith(('يوت ', 'yt ')))
def yt_handler(message):
    msg = message.text.lower()
    sender_id = message.from_user.id

    if sender_id in cooldown and time.time() - cooldown[sender_id] < 10:
        return
    cooldown[sender_id] = time.time()

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
    try:
        audio_data = requests.get(audio_api, timeout=15)
    except Exception as e:
        bot.reply_to(message, "ما قدرت أتواصل ويا السيرفر.")
        logging.error(f"Download Error: {str(e)}")
        return

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

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    caption = f"{title}\nطلب بواسطة: {username}"

    bot.send_audio(message.chat.id, open(temp_file, 'rb'), caption=caption)
    os.remove(temp_file)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

print("جاري تشغيل البوت...")
bot.polling(non_stop=True)
