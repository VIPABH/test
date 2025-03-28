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

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_video(query: str):
    ydl_opts = {
        'format': 'best',  # تحميل الفيديو بأفضل جودة بدون تعديل
        'quiet': True,     # إخفاء الرسائل أثناء التحميل
        'noplaylist': True,  # عدم تحميل قوائم التشغيل
        'cookiefile': 'cookies.txt',  # استخدام الكوكيز إذا كانت مطلوبة
        'noprogress': True,  # إخفاء شريط التقدم
        'default_search': 'ytsearch',  # البحث في يوتيوب
        'outtmpl': '%(id)s.%(ext)s',  # استخدام اسم الفيديو كما هو
        'progress_hooks': [lambda d: None],  # إخفاء التقدم
        'concurrent_fragment_downloads': 100,  # تحميل الأجزاء في نفس الوقت
        'max_filesize': 50 * 1024 * 1024,  # تحديد الحد الأقصى للحجم (50 ميجابايت)
        'socket_timeout': 30,  # تقليل التأخير
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        output_file = ydl.prepare_filename(info)  # الحصول على اسم الملف
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return output_file  # إرجاع مسار الملف المحمل

@client.on(events.NewMessage(pattern='يوت'))
async def handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond('ارسل الرابط أو النص المطلوب.')
    query = msg_parts[1]
    video_file = await download_video(query)
    if video_file:
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            video_file, 
            caption='**[Enjoy dear]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(video_file)
    else:
        await event.respond("فشل تحميل الفيديو.")

client.run_until_disconnected()
