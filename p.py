from youtubesearchpython import VideosSearch
import pytube, os
from telethon import TelegramClient, events

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# البحث عن الفيديوهات
@client.on(events.NewMessage(pattern='/download'))
async def download_video(event):
    query = event.message.text.replace('/download', '').strip()  # استلام استعلام البحث من المستخدم
    if query:
        # البحث عن الفيديو
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()
        
        # استخراج رابط الفيديو
        video_url = results['result'][0]['link']

        # تنزيل الفيديو باستخدام pytube
        yt = pytube.YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        file_path = f"{yt.title}.mp4"  # اسم الملف الذي سيتم تنزيله
        stream.download(filename=file_path)

        # إرسال الفيديو للمستخدم
        await event.reply('تم تنزيل الفيديو بنجاح!')
        await client.send_file(event.sender_id, file_path)
    else:
        await event.reply('يرجى إدخال اسم الفيديو بعد الأمر /download.')

# تشغيل البوت
client.run_until_disconnected()
