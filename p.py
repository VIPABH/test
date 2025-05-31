import os
from telethon import TelegramClient, events
import yt_dlp

# تحميل القيم من المتغيرات البيئية (Environment Variables)
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# دالة لتحميل الصوت من ساوند كلاود (أو أي رابط مدعوم)
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

# حدث عند استقبال رسالة تبدأ بـ ".صوت "
@client.on(events.NewMessage(pattern=r'^\.صوت (.+)'))
async def soundcloud_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f'🔍 جاري البحث وتحميل الصوت لـ: {query} ...')

    # **هنا يجب عليك البحث عن رابط مباشر لمقطع الصوت في ساوند كلاود**
    # للشرح، سأضع رابطًا ثابتًا كمثال (استبدل هذا بالرابط الفعلي بناءً على البحث)
    soundcloud_url = 'https://soundcloud.com/artist/track'  # استبدل بالرابط الصحيح

    output_file = f'downloads/{event.sender_id}_{event.id}.mp3'
    try:
        download_audio(soundcloud_url, output_file)
        await client.send_file(event.chat_id, output_file, caption=f'صوت من ساوند كلاود: {query}')
    except Exception as e:
        await event.reply(f'⚠️ حدث خطأ أثناء التحميل أو الإرسال: {e}')
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

print("🤖 بوت تيليجرام يعمل...")

client.run_until_disconnected()
