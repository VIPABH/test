import os
from telethon import TelegramClient, events
import yt_dlp

# تحميل القيم من المتغيرات البيئية
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@client.on(events.NewMessage(pattern=r'^\.صوت (.+)'))
async def soundcloud_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f'🔍 جاري تحميل الصوت لـ: {query} ...')

    # **رابط ثابت لمقطع صوتي في ساوند كلاود للاختبار**
    # استبدل الرابط بالرابط الذي تريد تحميله
    soundcloud_url = 'https://soundcloud.com/forss/flickermood'

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{event.sender_id}_{event.id}.mp3')

    try:
        download_audio(soundcloud_url, output_file)
        if os.path.exists(output_file):
            await client.send_file(event.chat_id, output_file, caption=f'🎵 صوت من ساوند كلاود: {query}')
        else:
            await event.reply("⚠️ لم يتم إنشاء ملف الصوت بنجاح.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء التحميل أو الإرسال:\n{e}")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

print("🤖 بوت تيليجرام يعمل...")

client.run_until_disconnected()
