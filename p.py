import os
from telethon import TelegramClient, events
import yt_dlp
import requests
import re

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

def get_first_soundcloud_track(query):
    search_url = f"https://m.soundcloud.com/search?q={query}"
    res = requests.get(search_url)
    if res.status_code != 200:
        return None
    urls = re.findall(r'data-testid="cell-entity-link" href="([^"]+)"', res.text)
    if not urls:
        return None
    return f"https://soundcloud.com{urls[0]}"

@client.on(events.NewMessage(pattern=r'^\.صوت (.+)'))
async def soundcloud_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f'🔍 جاري البحث وتحميل الصوت لـ: {query} ...')

    soundcloud_url = get_first_soundcloud_track(query)
    if not soundcloud_url:
        await event.reply('⚠️ لم أتمكن من العثور على مقطع صوتي لهذا البحث.')
        return

    output_file = f'downloads/{event.sender_id}_{event.id}.mp3'
    try:
        download_audio(soundcloud_url, output_file)
        await client.send_file(event.chat_id, output_file, caption=f'صوت من ساوند كلاود: {query}')
    except Exception as e:
        await event.reply(f'⚠️ حدث خطأ أثناء التحميل أو الإرسال: {e}')
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

print("🤖 بوت تيليجرام يعمل...")

client.run_until_disconnected()
