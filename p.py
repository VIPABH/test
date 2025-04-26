import logging
import os
import requests
import time
import re
import telebot
import json

from telebot import types

bot_token = os.getenv('BOT_TOKEN')

YOUTUBE_API_KEY = 'AIzaSyDLp3YbxDpGMGHmGS7Kx39GLqHmYJ5b8XE'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

bot = telebot.TeleBot(bot_token)

cooldown = {}
logging.basicConfig(filename='errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

SAVED_AUDIOS_FILE = 'saved_audios.json'

if os.path.exists(SAVED_AUDIOS_FILE):
    with open(SAVED_AUDIOS_FILE, 'r') as f:
        saved_audios = json.load(f)
else:
    saved_audios = {}

@bot.message_handler(commands=['start'])
def start(message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    welcome_message = f"مرحبًا {username}!\nأنا بوت يوتيوب، أساعدك بتحميل أغاني يوتيوب.\nاكتب 'يوت' أو 'yt' متبوعًا باسم الأغنية أو رابطها."
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("اضفني إلى مجموعاتك", url="https://t.me/YOUR_BOT_USERNAME")
    markup.add(button)
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower().startswith(('يوت ', 'yt ')))
def yt_handler(message):
    msg = message.text.strip()
    sender_id = message.from_user.id

    if sender_id in cooldown and time.time() - cooldown[sender_id] < 10:
        return
    cooldown[sender_id] = time.time()

    if " " not in msg:
        bot.reply_to(message, "❗ الرجاء كتابة اسم أو رابط اليوتيوب بعد الأمر.")
        return

    query = msg.split(" ", 1)[1].strip()

    video_id, title = None, None
    youtube_url = None

    found_links = find_urls(query)
    if found_links:
        youtube_url = found_links[0]
        if 'youtu.be/' in youtube_url:
            video_id = youtube_url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in youtube_url:
            video_id = youtube_url.split('v=')[1].split('&')[0]

    if not video_id:
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 1,
            'type': 'video'
        }
        try:
            response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=60)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            logging.error(f"Search Error: {str(e)}")
            bot.reply_to(message, "❗ حدث خطأ أثناء الاتصال بواجهة يوتيوب.")
            return

        if 'items' not in result or not result['items']:
            bot.reply_to(message, "❌ لم يتم العثور على نتائج.")
            return

        video_id = result['items'][0]['id']['videoId']
        title = result['items'][0]['snippet']['title']
        youtube_url = f"https://youtu.be/{video_id}"
    else:
        title = fetch_video_title(video_id) or "مقطع بدون عنوان"

    if not youtube_url:
        bot.reply_to(message, "❗ لم يتم العثور على رابط فيديو صالح.")
        return

    if youtube_url in saved_audios:
        file_path = saved_audios[youtube_url]['file_path']
        title = saved_audios[youtube_url]['title']

        if os.path.exists(file_path):
            username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{sender_id}"
            caption = f"{title}\nطلب بواسطة: {username}"
            bot.send_audio(message.chat.id, open(file_path, 'rb'), caption=caption)
            return
        else:
            del saved_audios[youtube_url]
            save_database()

    safe_title = sanitize_filename(title)[:50]
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

    temp_file = f"downloads/{safe_title}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(audio_response.content)

    if os.path.getsize(temp_file) > 80 * 1024 * 1024:
        os.remove(temp_file)
        bot.reply_to(message, "⚠️ الملف الصوتي أكبر من 40 ميغابايت، لا يمكن إرساله.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{sender_id}"
    caption = f"{title}\nطلب بواسطة: {username}"

    bot.send_audio(message.chat.id, open(temp_file, 'rb'), caption=caption)

    saved_audios[youtube_url] = {
        'video_id': video_id,
        'file_path': temp_file,
        'title': title
    }
    save_database()

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def save_database():
    with open(SAVED_AUDIOS_FILE, 'w') as f:
        json.dump(saved_audios, f, indent=4, ensure_ascii=False)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

def fetch_video_title(video_id):
    try:
        params = {
            'part': 'snippet',
            'id': video_id,
            'key': YOUTUBE_API_KEY
        }
        response = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['snippet']['title']
    except Exception as e:
        logging.error(f"Fetch Title Error: {str(e)}")
    return None

print("جاري تشغيل البوت...")
bot.polling(non_stop=True)
