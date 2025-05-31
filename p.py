import os
import glob
import subprocess
from telethon import events

DOWNLOADS_DIR = "downloads"

@bot.on(events.NewMessage(pattern=r'^\.صوت (.+)'))
async def audio_handler(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن: {query}")

    try:
        # تأكد من وجود مجلد التنزيل
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        # مسح الملفات القديمة
        for old_file in glob.glob(f"{DOWNLOADS_DIR}/*.mp3"):
            os.remove(old_file)

        output_path = os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s")

        # تحميل الصوت
        result = subprocess.run(
            ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o", output_path, f"ytsearch1:{query}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            await event.reply(f"⚠️ خطأ في yt-dlp:\n{result.stderr}")
            return

        # العثور على الملف الناتج
        files = glob.glob(f"{DOWNLOADS_DIR}/*.mp3")
        if not files:
            await event.reply("⚠️ لم يتم العثور على أي ملف صوتي.")
            return

        mp3_file = files[0]

        # التحقق من الحجم (Telegram limit ~50MB)
        size_mb = os.path.getsize(mp3_file) / (1024 * 1024)
        if size_mb > 49:
            await event.reply(f"⚠️ الملف كبير جدًا: {size_mb:.2f}MB، الحد المسموح 49MB.")
            return

        # الإرسال
        await bot.send_file(event.chat_id, file=mp3_file, reply_to=event.id)

        # حذف الملف
        os.remove(mp3_file)

    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ: {e}")
