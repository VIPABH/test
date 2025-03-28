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
async def download_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
        }],
        'noprogress': True,
        'cookiefile': 'cookies.txt',  # 🔹 إضافة ملف الكوكيز
    }

    try:
        search_query = query if "http" in query else f"ytsearch:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)

            if not info or 'entries' in info and not info['entries']:
                raise Exception("⚠️ لم يتم العثور على نتائج، حاول استخدام كلمات مختلفة.")

            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit('.', 1)[0] + ".mp3"

        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            raise FileNotFoundError("⚠️ فشل تحميل الملف الصوتي!")

        return audio_file
    except Exception as e:
        with open("log.txt", "a") as log_file:
            log_file.write(f"خطأ: {e}\n")
        return None

@client.on(events.NewMessage(pattern='تحميل'))
async def handler(event):
    try:
        msg_parts = event.message.text.split(' ', 1)
        if len(msg_parts) < 2:
            await event.respond('❌ يرجى إرسال رابط أو كتابة عنوان الأغنية بعد "تحميل".')
            return

        query = msg_parts[1]
        await event.respond(f'⏳ جارٍ البحث عن: "{query}" وتحميل الصوت...')

        audio_file = await download_audio(query)

        if audio_file:
            await event.client.send_file(event.chat_id, audio_file, voice_note=True)
            os.remove(audio_file)  # حذف الملف بعد الإرسال
        else:
            await event.respond("❌ فشل تحميل الصوت، تحقق من الرابط أو حاول لاحقًا.")

    except Exception as e:
        await event.respond(f'⚠️ خطأ: {e}')

client.run_until_disconnected()
