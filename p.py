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

# ملف تخزين الأغاني
SAVED_AUDIOS_FILE = 'saved_audios.json'

# تحميل قاعدة البيانات اذا موجودة
if os.path.exists(SAVED_AUDIOS_FILE):
    with open(SAVED_AUDIOS_FILE, 'r') as f:
        saved_audios = json.load(f)
else:
    saved_audios = {}

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

    # بحث بالرابط لو المستخدم دخل رابط مباشر
    found_links = find_urls(query)
    video_id = None
    if found_links:
        # رابط موجود مباشرة
        video_url = found_links[0]
        if 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1]
        elif 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]

    if not video_id:
        # لا، مو رابط.. لازم بحث
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 1,
            'type': 'video'
        }
        r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=60).json()

        if 'items' not in r or len(r['items']) == 0:
            bot.reply_to(message, "ما لكيت شي لهالاسم.")
            return

        video_id = r['items'][0]['id']['videoId']
        title = r['items'][0]['snippet']['title']
    else:
        # عندنا video_id من الرابط
        title = query  # اسم البحث الحالي

    youtube_url = f"https://youtu.be/{video_id}"

    # تحقق اذا الرابط موجود بالمحفوظات
    if youtube_url in saved_audios:
        file_path = saved_audios[youtube_url]['file_path']
        title = saved_audios[youtube_url]['title']

        if os.path.exists(file_path):
            username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
            caption = f"{title}\nطلب بواسطة: {username}"
            bot.send_audio(message.chat.id, open(file_path, 'rb'), caption=caption)
            return
        else:
            # اذا الملف المحفوظ اختفى نحذفه من قاعدة البيانات
            del saved_audios[youtube_url]
            save_database()

    # تحميل جديد اذا مو موجود
    safe_title = sanitize_filename(title)[:50]
    audio_api = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

    try:
        audio_data = requests.get(audio_api, timeout=60)
    except Exception as e:
        bot.reply_to(message, f"ما قدرت أتواصل ويا السيرفر. {e}")
        logging.error(f"Download Error: {str(e)}")
        return

    if audio_data.status_code != 200:
        bot.reply_to(message, "للأسف، ما قدرت أنزل الصوت. يمكن السيرفر فيه مشكلة.")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    temp_file = f"downloads/{safe_title}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(audio_data.content)

    if os.path.getsize(temp_file) > 80 * 1024 * 1024:
        os.remove(temp_file)
        bot.reply_to(message, "الملف أكبر من 40MB، ما أقدر أرسله.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{message.from_user.id}"
    caption = f"{title}\nطلب بواسطة: {username}"

    bot.send_audio(message.chat.id, open(temp_file, 'rb'), caption=caption)

    # حفظ البيانات بالرابط
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
    # استخراج الروابط من النص
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

print("جاري تشغيل البوت...")
bot.polling(non_stop=True)

