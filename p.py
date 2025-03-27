import os
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

async def download_audio(url: str):
    # تعيين اسم الملف بناءً على الرابط أو تحديد اسم ثابت
    output_file = "audio.mp3"

    ydl_opts = {
        'format': 'worstaudio',  # اختيار أسوأ جودة صوت
        'quiet': False,  # تفعيل السجلات لتشخيص الأخطاء
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # استخدام ملفات الكوكيز إن لزم الأمر
        'outtmpl': output_file,  # حفظ الملف الصوتي باسم audio.mp3
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # تحويل الملف إلى صيغة MP3
            'preferredquality': '64',  # جودة الصوت 64kbps
            'nopostoverwrites': True,  # منع إضافة امتداد mp3 مرتين
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # التحقق من المعلومات دون تحميل
            if not info:
                raise Exception("لم يتمكن yt-dlp من جلب المعلومات")

            ydl.download([url])  # تحميل المقطع الصوتي

        # التحقق من وجود الملف
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise FileNotFoundError("فشل تحميل الملف الصوتي")

        return output_file
    except Exception as e:
        with open("log.txt", "a") as log_file:
            log_file.write(f"خطأ: {e}\n")
        return None

@client.on(events.NewMessage(pattern='/تحميل'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('يرجى إرسال رابط الفيديو بعد /تحميل')
            return
        
        await event.respond('جارٍ التحميل...')
        audio_file = await download_audio(msg_parts[1])

        if audio_file:
            # إرسال الملف الصوتي كـ ملف MP3 مع تحديد اسم الملف واسم الفنان
            await event.client.send_file(
                event.chat_id, 
                audio_file, 
                file_name="audio.mp3",  # تحديد اسم الملف
                thumb="https://t.me/VIPABH/1242",  # تحديد الصورة المصغرة (إذا كانت موجودة)
                caption="الفنان: Anonymous"  # إضافة اسم الفنان
            )
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")

    except Exception as e:
        await event.respond(f'خطأ: {e}')

@client.on(events.NewMessage(pattern='/فويس'))
async def handle_voice(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('يرجى إرسال رابط الفيديو بعد /فويس')
            return

        await event.respond('جارٍ التحميل...')
        audio_file = await download_audio(msg_parts[1])

        if audio_file:
            # إرسال الملف الصوتي كـ ملاحظة صوتية فقط مع تحديد اسم الملف واسم الفنان
            await event.client.send_file(
                event.chat_id, 
                audio_file, 
                voice_note=True,
                file_name="audio.mp3",  # تحديد اسم الملف
                thumb="https://t.me/VIPABH/1242",  # تحديد الصورة المصغرة (إذا كانت موجودة)
                caption="الفنان: Anonymous"  # إضافة اسم الفنان
            )
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")
    except Exception as e:
        await event.respond(f'خطأ: {e}')

client.run_until_disconnected()
