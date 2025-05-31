import os
import requests
from telethon import TelegramClient, events
import yt_dlp
from bs4 import BeautifulSoup

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def search_soundcloud(query):
    search_url = f"https://soundcloud.com/search/sounds?q={requests.utils.quote(query)}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    # البحث عن روابط الأصوات باستخدام السمات الصحيحة
    results = soup.find_all('a', href=True)
    for link in results:
        href = link['href']
        # روابط مسارات ساوند كلاود تتبع الشكل: /artist/track
        if href.count('/') == 2 and href.startswith('/'):
            full_url = f"https://soundcloud.com{href}"
            # يمكن هنا إضافة تحقق برأس HTTP للتأكد من صحة الرابط
            r = requests.head(full_url)
            if r.status_code == 200:
                return full_url
    return None

@client.on(events.NewMessage(pattern=r'^\.صوت (.+)'))
async def soundcloud_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f'🔍 جاري البحث عن الصوت لـ: {query} ...')

    soundcloud_url = search_soundcloud(query)
    if not soundcloud_url:
        await event.reply('⚠️ لم يتم العثور على نتائج لصوت بهذا الاسم.')
        return

    await event.reply(f'✅ تم العثور على رابط: {soundcloud_url}\nجارٍ التحميل...')

    output_file = f'downloads/{event.sender_id}_{event.id}.mp3'

    try:
        download_audio(soundcloud_url, output_file)
        await client.send_file(event.chat_id, output_file, caption=f'🎵 الصوت المطلوب: {query}')
    except Exception as e:
        await event.reply(f'⚠️ حدث خطأ أثناء التحميل أو الإرسال: {e}')
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

print("🤖 بوت تيليجرام يعمل...")

client.run_until_disconnected()
