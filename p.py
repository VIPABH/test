from telethon import TelegramClient, events
import yt_dlp
import os

# ✨ استبدل هذه القيم بالمعلومات الخاصة بك
API_ID = 123456
API_HASH = "abcdef1234567890"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# ✅ إنشاء جلسة البوت
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🎵 إعداد خيارات yt_dlp لتنزيل الصوت
ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{  
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

# 📥 استقبال الأوامر ومعالجة الرابط
@bot.on(events.NewMessage(pattern='/download (.+)'))
async def download_audio(event):
    url = event.pattern_match.group(1)  # استخراج الرابط من الرسالة
    await event.reply("⏳ جاري تحميل الصوت...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # تحميل الصوت
            file_name = ydl.prepare_filename(info).replace('.webm', '.m4a')  # اسم الملف النهائي

        # 📤 إرسال الملف الصوتي
        await event.reply("✅ تم التحميل، جاري الإرسال...")
        await event.client.send_file(event.chat_id, file_name, caption="🎶 الصوت المطلوب")

        # 🗑️ حذف الملف بعد الإرسال لتوفير المساحة
        os.remove(file_name)

    except Exception as e:
        await event.reply(f"❌ حدث خطأ: {str(e)}")

# 🚀 تشغيل البوت
print("🤖 البوت يعمل...")
bot.run_until_disconnected()
