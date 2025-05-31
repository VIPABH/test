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

    # هنا يجب استبدال الرابط بالرابط الحقيقي الناتج من البحث
    soundcloud_url = 'https://soundcloud.com/artist/track'  # استبدل بالرابط الصحيح

    base_output_file = f'downloads/{event.sender_id}_{event.id}.mp3'
    converted_file = base_output_file + ".mp3"  # yt-dlp يضيف .mp3 ثانية

    try:
        download_audio(soundcloud_url, base_output_file)

        # قائمة الملفات التي قد تم إنشاؤها
        files_to_send = []
        if os.path.exists(base_output_file):
            files_to_send.append(base_output_file)
        if os.path.exists(converted_file):
            files_to_send.append(converted_file)

        if not files_to_send:
            await event.reply('⚠️ لم يتم إنشاء ملف الصوت بنجاح.')
            return

        # إرسال الملفات واحدًا تلو الآخر
        for fpath in files_to_send:
            await client.send_file(event.chat_id, fpath, caption=f'صوت من ساوند كلاود: {query}')

        # حذف الملفات بعد الإرسال
        for fpath in files_to_send:
            try:
                os.remove(fpath)
            except Exception as e:
                print(f"خطأ عند حذف الملف {fpath}: {e}")

    except Exception as e:
        await event.reply(f'⚠️ حدث خطأ أثناء التحميل أو الإرسال: {e}')

print("🤖 بوت تيليجرام يعمل...")

client.run_until_disconnected()
