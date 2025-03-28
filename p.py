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

# تحميل الفيديو والصوت
async def download_video_and_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',  # تحميل الصوت بأعلى جودة
        'quiet': True,  # إخفاء التقدم
        'noplaylist': True,  # عدم تحميل قوائم التشغيل
        'cookiefile': 'cookies.txt',  # إذا كانت الكوكيز مطلوبة
        'noprogress': True,  # إخفاء شريط التقدم
        'default_search': 'ytsearch',  # البحث في يوتيوب
        'outtmpl': '%(id)s.%(ext)s',  # اسم الملف وفقًا لـ ID
        'extractaudio': True,  # استخراج الصوت فقط
        'prefer_ffmpeg': True,  # استخدام FFmpeg إذا كان متاحًا
        'postprocessors': [],  # لا نحتاج إلى معالج إضافي
        'progress_hooks': [lambda d: None],  # إخفاء التقدم بشكل كامل
        'concurrent_fragment_downloads': 100,  # تحميل أجزاء متعددة في وقت واحد
        'max_filesize': 50 * 1024 * 1024,  # الحد الأقصى للحجم (50 ميجابايت)
        'socket_timeout': 30,  # مهلة الاتصال
        'audio_quality': '0',  # تحميل الصوت بأعلى جودة متاحة
        'audio_only': True,  # تحميل الصوت فقط
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)  # استخراج معلومات الفيديو وتحميله
            if 'entries' in info:
                info = info['entries'][0]  # اختر أول نتيجة
            output_file = ydl.prepare_filename(info)  # تحديد اسم الملف
            video_file = output_file.rsplit('.', 1)[0] + ".mp4"  # التأكد من أنه فيديو
            audio_file = output_file.rsplit('.', 1)[0] + ".mp3"  # التأكد من أنه MP3
            return video_file, audio_file
        except yt_dlp.utils.DownloadError as e:
            print(f"Error: {e}")
            return None, None

# تحميل الصوت فقط كـ MP3
async def download_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',  # تحميل الصوت بأعلى جودة
        'quiet': True,  # إخفاء التقدم
        'noplaylist': True,  # عدم تحميل قوائم التشغيل
        'cookiefile': 'cookies.txt',  # إذا كانت الكوكيز مطلوبة
        'noprogress': True,  # إخفاء شريط التقدم
        'default_search': 'ytsearch',  # البحث في يوتيوب
        'outtmpl': '%(id)s.%(ext)s',  # اسم الملف وفقًا لـ ID
        'extractaudio': True,  # استخراج الصوت فقط
        'prefer_ffmpeg': True,  # استخدام FFmpeg إذا كان متاحًا
        'postprocessors': [],  # لا نحتاج إلى معالج إضافي
        'progress_hooks': [lambda d: None],  # إخفاء التقدم بشكل كامل
        'concurrent_fragment_downloads': 100,  # تحميل أجزاء متعددة في وقت واحد
        'max_filesize': 50 * 1024 * 1024,  # الحد الأقصى للحجم (50 ميجابايت)
        'socket_timeout': 30,  # مهلة الاتصال
        'audio_quality': '0',  # تحميل الصوت بأعلى جودة متاحة
        'audio_only': True,  # تحميل الصوت فقط
    }

    if not query.startswith(("http://", "https://")):
        query = f"ytsearch:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)  # استخراج معلومات الفيديو وتحميله
            if 'entries' in info:
                info = info['entries'][0]  # اختر أول نتيجة
            output_file = ydl.prepare_filename(info)  # تحديد اسم الملف
            audio_file = output_file.rsplit('.', 1)[0] + ".mp3"  # التأكد من أنه MP3
            return audio_file
        except yt_dlp.utils.DownloadError as e:
            print(f"Error: {e}")
            return None

@client.on(events.NewMessage(pattern='فيديو'))
async def video_handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond('ارسل الرابط أو النص المطلوب.')
    query = msg_parts[1]
    video_file, audio_file = await download_video_and_audio(query)
    if video_file and audio_file:
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            video_file, 
            caption='**[استمتع بالفيديو والصوت]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        await event.client.send_file(
            event.chat_id, 
            audio_file, 
            caption='**[استمتع بالصوت]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(video_file)
        os.remove(audio_file)
    else:
        await event.respond("فشل تحميل الفيديو والصوت. تحقق من الرابط أو استعلم عن سبب المشكلة.")

@client.on(events.NewMessage(pattern='كلام'))
async def audio_handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond('ارسل الرابط أو النص المطلوب.')
    query = msg_parts[1]
    audio_file = await download_audio(query)
    if audio_file:
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            audio_file, 
            caption='**[استمتع بالصوت]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(audio_file)
    else:
        await event.respond("فشل تحميل الصوت. تحقق من الرابط أو استعلم عن سبب المشكلة.")

@client.on(events.NewMessage(pattern='يوت'))
async def mp3_handler(event):
    msg = await event.reply('🤌')
    msg_parts = event.message.text.split(' ', 1)
    if len(msg_parts) < 2:
        return await event.respond('ارسل الرابط أو النص المطلوب.')
    query = msg_parts[1]
    audio_file = await download_audio(query)  # تحميل الصوت فقط كـ MP3
    if audio_file:
        button = [Button.url("chanel", "https://t.me/sszxl")]
        await msg.delete()
        await event.client.send_file(
            event.chat_id, 
            audio_file, 
            caption='**[استمتع بالصوت MP3]**(https://t.me/VIPABH_BOT)', 
            buttons=button, 
            reply_to=event.message.id
        )
        os.remove(audio_file)
    else:
        await event.respond("فشل تحميل الصوت MP3. تحقق من الرابط أو استعلم عن سبب المشكلة.")

client.run_until_disconnected()
