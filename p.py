import logging
import os
import requests
import re
from telethon import events, TelegramClient

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

@ABH.on(events.NewMessage(pattern='يوت'))
async def download_video(event):
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

    video_api_url = f"http://167.99.211.62/youtube/api.php?video_id={video_id}"

    try:
        video_response = requests.get(video_api_url, timeout=60)
        video_response.raise_for_status()
    except Exception as e:
        logging.error(f"Download Video Error: {str(e)}")
        await event.reply(f"❌ حدث خطأ أثناء تحميل الفيديو: {e}")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    temp_file_path = f"downloads/{video_id}.mp4"
    
    with open(temp_file_path, 'wb') as f:
        f.write(video_response.content)

    if os.path.getsize(temp_file_path) > 50 * 1024 * 1024:  # يمكنك تعديل الحجم حسب الحاجة
        os.remove(temp_file_path)
        await event.reply("⚠️ الفيديو أكبر من 50 ميغابايت، لا يمكن إرساله.")
        return

    # إرسال الفيديو
    with open(temp_file_path, 'rb') as video:
        await event.client.send_file(
            event.chat_id, 
            video, 
            caption='**[استمتع بالفيديو]**(https://t.me/VIPABH_BOT)', 
            reply_to=event.message.id,
            force_document=False  # التأكد من إرسال الملف كفيديو وليس مستند
        )

    os.remove(temp_file_path)  # حذف الملف بعد الإرسال

def find_urls(text):
    url_regex = r"(https?://[^\s]+)"
    return re.findall(url_regex, text)

print("✅ جاري تشغيل البوت...")
ABH.run_until_disconnected()
