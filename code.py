from ABH import ABH as client
from telethon import TelegramClient, events
import instaloader
import os
import re
import tempfile


# -------- إعدادات Instaloader --------
TEMP_DIR = tempfile.gettempdir()
L = instaloader.Instaloader(download_videos=True, download_pictures=True, download_comments=False, save_metadata=False, compress_json=False)

# -------- إنشاء Client --------


# -------- وظيفة تنزيل الإنستاغرام --------
def download_instagram(url: str):
    shortcode_match = re.search(r"(?:/p/|/reel/|/tv/)([\w-]+)", url)
    if not shortcode_match:
        return None
    shortcode = shortcode_match.group(1)
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except instaloader.exceptions.InstaloaderException:
        return None

    target_dir = os.path.join(TEMP_DIR, shortcode)
    os.makedirs(target_dir, exist_ok=True)
    L.download_post(post, target=target_dir)

    for file in os.listdir(target_dir):
        if file.lower().endswith((".mp4", ".mov", ".jpg", ".png")):
            return os.path.join(target_dir, file)
    return None

# -------- حدث استقبال الرسائل --------
@client.on(events.NewMessage)
async def handler(event):
    message_text = event.message.message.strip()
    if message_text.lower() == "/start":
        await event.reply("أرسل رابط منشور أو ريل إنستاغرام، وسيتم تنزيله وإرساله لك.")
        return

    await event.respond("جاري تنزيل الملف...")

    file_path = download_instagram(message_text)
    if not file_path:
        await event.reply("لم أتمكن من تنزيل الملف. تأكد أن المنشور عام (public).")
        return

    try:
        if file_path.lower().endswith((".mp4", ".mov")):
            await client.send_file(event.sender_id, file_path, video_note=False)
        else:
            await client.send_file(event.sender_id, file_path)
    except Exception as e:
        await event.reply(f"حدث خطأ أثناء الإرسال: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# -------- تشغيل البوت --------
