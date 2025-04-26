import os
import requests
import re
import json
from pydub import AudioSegment  # مكتبة لتحويل الصوت
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerUser

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
bot = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
YOUTUBE_API_KEY = 'AIzaSyDLp3YbxDpGMGHmGS7Kx39GLqHmYJ5b8XE'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
SAVED_AUDIOS_FILE = 'saved_audios.json'
if os.path.exists(SAVED_AUDIOS_FILE):
    with open(SAVED_AUDIOS_FILE, 'r') as f:
        saved_audios = json.load(f)
else:
    saved_audios = {}

async def convert_to_mp3(file_path):
    mp3_path = file_path.rsplit('.', 1)[0] + '.mp3'
    if not file_path.endswith('.mp3'):
        audio = AudioSegment.from_file(file_path)
        audio.export(mp3_path, format='mp3')
        os.remove(file_path) 
        return mp3_path
    return file_path
@bot.on(events.NewMessage)
import os
import aiohttp
from mutagen.mp3 import MP3
from telethon.tl.types import DocumentAttributeAudio
from telethon import events

async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=60) as response:
            if response.status != 200:
                return None
            data = await response.read()
            with open(filename, 'wb') as f:
                f.write(data)
    return filename

def get_audio_duration(file_path):
    audio = MP3(file_path)
    return int(audio.info.length)

@bot.on(events.NewMessage)
async def yt_handler(event):
    try:
        uid = event.sender_id
        x = await event.reply('🔍 جاري البحث عن الصوت...')

        msg = event.raw_text.lower()
        if " " not in msg:
            await x.edit("❗ يرجى كتابة اسم المقطع أو الرابط بعد الأمر.")
            return

        query = msg.split(" ", 1)[1]

        # البحث عن الرابط إن وجد
        found_links = await find_urls(query)
        video_id, title = None, None

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
            async with aiohttp.ClientSession() as session:
                async with session.get(YOUTUBE_SEARCH_URL, params=params) as resp:
                    r = await resp.json()

            if 'items' not in r or len(r['items']) == 0:
                await x.edit("❌ لم يتم العثور على نتائج.")
                return

            video_id = r['items'][0]['id']['videoId']
            title = r['items'][0]['snippet']['title']
            youtube_url = f"https://youtu.be/{video_id}"
        else:
            youtube_url = f"https://youtu.be/{video_id}"
            title = query

        # إذا كان موجود مسبقًا
        if youtube_url in saved_audios:
            file_path = saved_audios[youtube_url]['file_path']
            title = saved_audios[youtube_url]['title']
            await x.delete()

            if os.path.exists(file_path):
                mp3_file = await convert_to_mp3(file_path)
                duration = get_audio_duration(mp3_file)
                attributes = [DocumentAttributeAudio(duration=duration, title=title, performer=f"ID:{uid}")]

                await bot.send_file(
                    event.chat_id,
                    file=mp3_file,
                    caption=f"{title}\nطلب بواسطة: {uid}",
                    attributes=attributes
                )
                return
            else:
                del saved_audios[youtube_url]
                await save_database()

        safe_title = sanitize_filename(title)[:50]
        audio_api = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

        # تحميل الملف الصوتي
        download_folder = "downloads"
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        temp_file = os.path.join(download_folder, f"{safe_title}.mp3")
        downloaded = await download_file(audio_api, temp_file)

        if not downloaded:
            await x.edit("❌ حدث خطأ أثناء تنزيل الملف الصوتي.")
            return

        if os.path.getsize(temp_file) > 80 * 1024 * 1024:
            os.remove(temp_file)
            await x.edit("⚠️ الملف أكبر من 40MB ولا يمكن إرساله.")
            return

        mp3_file = await convert_to_mp3(temp_file)
        duration = get_audio_duration(mp3_file)

        attributes = [DocumentAttributeAudio(duration=duration, title=title, performer=f"ID:{uid}")]

        await bot.send_file(
            event.chat_id,
            file=mp3_file,
            caption=f"{title}\nطلب بواسطة: {uid}",
            attributes=attributes
        )

        saved_audios[youtube_url] = {
            'video_id': video_id,
            'file_path': mp3_file,
            'title': title
        }
        await save_database()
        await x.delete()

    except Exception as e:
        await event.reply(f"❗ حصل خطأ غير متوقع: {str(e)}")
    saved_audios[youtube_url] = {
        'video_id': video_id,
        'file_path': mp3_file,
        'title': title
    }
    await save_database()

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

async def save_database():
    with open(SAVED_AUDIOS_FILE, 'w') as f:
        json.dump(saved_audios, f, indent=4, ensure_ascii=False)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

bot.run_until_disconnected()
