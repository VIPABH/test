import logging
import os
import requests
import re
from telethon import events, TelegramClient
from mutagen.mp3 import MP3

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='يوت'))
async def download_audio(event):
    msg = event.text.strip()
    found_links = find_urls(msg)
    
    if not found_links:        
        await event.reply('❗ لم أتمكن من العثور على رابط يوتيوب.')
        return
    
    youtube_url = found_links[0]
    
    if 'youtu.be/' in youtube_url:
        video_id = youtube_url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/watch?v=' in youtube_url:
        video_id = youtube_url.split('v=')[1].split('&')[0]
    else:
        await event.reply('❗ الرابط غير صحيح.')
        return

    audio_api_url = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

    try:
        audio_response = requests.get(audio_api_url, timeout=60)
        audio_response.raise_for_status()
    except Exception as e:
        logging.error(f"Download Audio Error: {str(e)}")
        await event.reply(f"❌ حدث خطأ أثناء تحميل الملف الصوتي: {e}")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    temp_file_path = f"downloads/{video_id}.mp3"
    
    with open(temp_file_path, 'wb') as f:
        f.write(audio_response.content)

    if os.path.getsize(temp_file_path) > 40 * 1024 * 1024:
        os.remove(temp_file_path)
        await event.reply("⚠️ الملف الصوتي أكبر من 40 ميغابايت، لا يمكن إرساله.")
        return
        await event.client.send_file(
            event.chat_id, 
            audio, 
            caption='**[استمتع بالصوت]**(https://t.me/VIPABH_BOT)', 
            reply_to=event.message.id
        )

    os.remove(temp_file_path)

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

print("✅ جاري تشغيل البوت...")
ABH.run_until_disconnected()
