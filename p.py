import os
from telethon import TelegramClient, events
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("❌ يرجى ضبط API_ID, API_HASH، و BOT_TOKEN في ملف .env")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def download_audio(search_query: str):
    output_file = "audio.mp3"
    cookies_file = 'cookies.txt'  # تأكد من أن هذا هو اسم ملف الكوكيز الخاص بك

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,  # تفعيل السجلات
        'noplaylist': True,
        'outtmpl': output_file,
        'extractaudio': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
            'nopostoverwrites': True,  # لتجنب إضافة الامتداد مرتين
        }],
    }

    # إضافة الكوكيز إذا كان الملف موجودًا
    if os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_url = f"ytsearch:{search_query}"
            info = ydl.extract_info(search_url, download=False)

            if not info or 'entries' not in info or len(info['entries']) == 0:
                raise Exception("❌ لم يتم العثور على أي نتائج للبحث.")

            video_url = info['entries'][0]['url']
            ydl.download([video_url])

        # التحقق من وجود الملف الصوتي
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise FileNotFoundError("❌ فشل تحميل الملف الصوتي.")

        return output_file
    except Exception as e:
        with open("log.txt", "a") as log_file:
            log_file.write(f"⚠️ خطأ: {e}\n")
        return None

@client.on(events.NewMessage(pattern='/تحميل'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('❌ ارسل النص بعد /تحميل')
            return
        
        await event.respond('⏳ جارٍ التحميل...')

        # تمرير النص إلى دالة البحث
        audio_file = await download_audio(msg_parts[1])

        if audio_file:
            await event.client.send_file(event.chat_id, audio_file, voice_note=True) 
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("❌ فشل تحميل الصوت، تحقق من النص أو حاول لاحقًا.")

    except Exception as e:
        await event.respond(f'⚠️ خطأ: {e}')

client.run_until_disconnected()
