import os
import yt_dlp
import validators
from telethon import TelegramClient, events
from dotenv import load_dotenv
import uuid  # لإنشاء أسماء ملفات فريدة

# تحميل المتغيرات من .env
load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(url):
    if not validators.url(url):
        return None, "الرابط غير صالح."

    file = f"{uuid.uuid4()}.mp3"  # اسم ملف عشوائي لمنع التعارض

    # إعدادات yt_dlp
    opts = {
        'format': 'bestaudio',
        'outtmpl': file,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
    }

    # التحقق من وجود ملف الكوكيز قبل استخدامه
    cookies_file = 'www.youtube.com_cookies.txt'
    if os.path.exists(cookies_file):
        opts['cookiefile'] = cookies_file

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"خطأ أثناء التنزيل: {e}")
        return None, "حدث خطأ أثناء تحميل الصوت."

    return (file, None) if os.path.exists(file) else (None, "فشل تحميل الصوت.")

@client.on(events.NewMessage(pattern='/تحميل'))
async def handler(event):
    msg = event.message.text.split(' ', 1)
    
    if len(msg) < 2:
        return await event.respond('❌ يرجى إرسال رابط يوتيوب بعد الأمر /تحميل')

    await event.respond('⏳ جارٍ التحميل...')
    audio, error = await download_audio(msg[1])

    if audio:
        await event.client.send_file(event.chat_id, audio)
        os.remove(audio)  # حذف الملف بعد الإرسال
    else:
        await event.respond(f'❌ {error}')

client.run_until_disconnected()
