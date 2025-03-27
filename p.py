import os
import re
from telethon import TelegramClient, events
from pytube import YouTube
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# إعداد بيانات API تيليجرام
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# التأكد من إدخال البيانات
if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN في ملف .env")

# إنشاء العميل
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# تحويل روابط Shorts إلى صيغة قابلة للتحميل
def fix_youtube_url(url):
    match = re.search(r"(?:youtube\.com\/shorts\/|youtu\.be\/)([\w-]+)", url)
    if match:
        return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

# دالة تحميل الصوت
async def download_audio(url: str):
    try:
        url = fix_youtube_url(url)  # تصحيح رابط Shorts
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        if not audio_stream:
            raise Exception("لم يتم العثور على مسار صوتي")

        output_file = "anymous.mp3"
        audio_stream.download(filename=output_file)

        # التأكد من أن الملف تم تحميله
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise FileNotFoundError("فشل تحميل الملف الصوتي")

        return output_file
    except Exception as e:
        with open("log.txt", "a") as log_file:
            log_file.write(f"خطأ: {e}\n")
        return None

# عند إرسال /تحميل مع رابط يوتيوب، يقوم البوت بإرسال الملف الصوتي
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
            await event.client.send_file(event.chat_id, audio_file, file_name="anymous.mp3")
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")

    except Exception as e:
        await event.respond(f'خطأ: {e}')

# عند إرسال /فويس مع رابط يوتيوب، يقوم البوت بإرسال الصوت كملاحظة صوتية
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
            await event.client.send_file(event.chat_id, audio_file, voice_note=True)
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")

    except Exception as e:
        await event.respond(f'خطأ: {e}')

# تشغيل البوت
client.run_until_disconnected()
