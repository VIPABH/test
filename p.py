import os
import asyncio
from telethon.tl.custom import Button
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")
import yt_dlp
import os
from telethon import events
from telethon.tl.custom import Button

async def download_video(query: str):
    ydl_opts = {
        'format': 'best',  
        'quiet': False, 
        'noplaylist': True, 
        'cookiefile': 'cookies.txt',  # ملف الكوكيز لتسجيل الدخول التلقائي
        'noprogress': True,  
        'default_search': 'ytsearch',  
        'outtmpl': '%(id)s.%(ext)s',  # تحديد اسم الملف
        'progress_hooks': [lambda d: None],  
        'concurrent_fragment_downloads': 100,  # عدد تحميلات الأجزاء المتوازية
        'max_filesize': 200 * 1024 * 1024,  # تحديد الحجم الأقصى للملف
        'socket_timeout': 30,
    }
    
    # التأكد من أن الاستعلام يحتوي على رابط صالح أو يتم تحويله إلى بحث
    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            output_file = ydl.prepare_filename(info)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file  # إعادة اسم الملف بعد التنزيل
        except yt_dlp.utils.DownloadError as e:
            print(f"Error: {e}")  
            return None

@ABH.on(events.NewMessage(pattern='فديو|فيديو'))
async def handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    query = msg_parts[1]
    
    # تحميل الفيديو بناءً على الاستعلام
    video_file = await download_video(query)
    if video_file:
        # إضافة زر في الرسالة بعد تحميل الفيديو
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            video_file, 
            caption='**[Enjoy dear]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(video_file)  # إزالة الملف بعد إرساله
    else:
        await event.respond("فشل تحميل الفيديو. تحقق من الرابط أو استعلم عن سبب المشكلة.")

ABH.run_until_disconnected()
