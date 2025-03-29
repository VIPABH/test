from youtubesearchpython import VideosSearch
import pytube, os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# البحث عن الفيديوهات
@client.on(events.NewMessage(pattern='/download'))
async def download_video(event):
    query = event.message.text.replace('/download', '').strip()  # استلام استعلام البحث من المستخدم
    if query:
        try:
            # البحث عن الفيديو
            videos_search = VideosSearch(query, limit=1)
            results = videos_search.result()

            if 'result' in results and len(results['result']) > 0:
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
                await event.reply('لم يتم العثور على أي فيديو باستخدام هذا الاستعلام.')
        except Exception as e:
            await event.reply(f"حدث خطأ أثناء البحث أو التنزيل: {e}")
    else:
        await event.reply('يرجى إدخال اسم الفيديو بعد الأمر /download.')

# تشغيل البوت
client.run_until_disconnected()
