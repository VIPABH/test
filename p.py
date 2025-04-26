import os
import re
import json
import time
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputWebDocument

# معلومات الاتصال
api_id = int(os.getenv("API_ID"))  # تأكد أن تضع متغيرات البيئة
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

# إعداد الكلاينت
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# روابط البحث
YOUTUBE_API_KEY = 'AIzaSyDLp3YbxDpGMGHmGS7Kx39GLqHmYJ5b8XE'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# ملفات التخزين
SAVED_AUDIOS_FILE = 'saved_audios.json'
cooldown = {}

# تحميل قاعدة بيانات الأغاني إذا موجودة
if os.path.exists(SAVED_AUDIOS_FILE):
    with open(SAVED_AUDIOS_FILE, 'r') as f:
        saved_audios = json.load(f)
else:
    saved_audios = {}

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

def save_database():
    with open(SAVED_AUDIOS_FILE, 'w') as f:
        json.dump(saved_audios, f, indent=4, ensure_ascii=False)

@bot.on(events.NewMessage(pattern=r'^(يوت|yt)\s+(.+)', outgoing=False))
async def yt_handler(event):
    sender = await event.get_sender()
    sender_id = sender.id

    if sender_id in cooldown and time.time() - cooldown[sender_id] < 10:
        return
    cooldown[sender_id] = time.time()

    query = event.pattern_match.group(2)

    found_links = find_urls(query)
    video_id = None
    if found_links:
        video_url = found_links[0]
        if 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1]
        elif 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]

    if not video_id:
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 1,
            'type': 'video'
        }
        r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=60).json()

        if 'items' not in r or len(r['items']) == 0:
            await event.reply("ما لكيت شي لهالاسم.")
            return

        video_id = r['items'][0]['id']['videoId']
        title = r['items'][0]['snippet']['title']
        youtube_url = f"https://youtu.be/{video_id}"
    else:
        youtube_url = f"https://youtu.be/{video_id}"
        title = query

    # تحقق من الحفظ المسبق
    if youtube_url in saved_audios:
        file_path = saved_audios[youtube_url]['file_path']
        title = saved_audios[youtube_url]['title']

        if os.path.exists(file_path):
            username = f"@{sender.username}" if sender.username else f"ID:{sender.id}"
            caption = f"{title}\nطلب بواسطة: {username}"
            await bot.send_file(event.chat_id, file_path, caption=caption)
            return
        else:
            del saved_audios[youtube_url]
            save_database()

    safe_title = sanitize_filename(title)[:50]
    audio_api = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

    try:
        audio_data = requests.get(audio_api, timeout=60)
    except Exception as e:
        await event.reply(f"ما قدرت أتواصل ويا السيرفر. {e}")
        return

    if audio_data.status_code != 200:
        await event.reply("للأسف، ما قدرت أنزل الصوت. يمكن السيرفر فيه مشكلة.")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    temp_file = f"downloads/{safe_title}.mp3"
    with open(temp_file, 'wb') as f:
        f.write(audio_data.content)

    if os.path.getsize(temp_file) > 80 * 1024 * 1024:
        os.remove(temp_file)
        await event.reply("الملف أكبر من 40MB، ما أقدر أرسله.")
        return

    username = f"@{sender.username}" if sender.username else f"ID:{sender.id}"
    caption = f"{title}\nطلب بواسطة: {username}"

    await bot.send_file(event.chat_id, temp_file, caption=caption)

    # حفظ البيانات
    saved_audios[youtube_url] = {
        'video_id': video_id,
        'file_path': temp_file,
        'title': title
    }
    save_database()

print("✅ البوت يعمل بنجاح باستخدام Telethon ...")
bot.run_until_disconnected()
