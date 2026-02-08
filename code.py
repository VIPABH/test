import yt_dlp
import os
import asyncio
import glob
import time
from ABH import *
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

# إعدادات خاصة لإنستغرام لتجنب الحظر بدون كوكيز
INSTA_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'format': 'best',
    'http_headers': {
        'User-Agent': 'Instagram 219.0.0.12.117 Android (28/9; 480dpi; 1080x1920; Xiaomi/Redmi; M2003J15SC; merlin; mt6768; en_US; 329521391)',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-IG-App-ID': '936619743392459', # ضروري جداً لتخطي حماية إنستا
    },
}

@ABH.on(events.NewMessage)
async def smart_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🔄 جاري محاولة جلب المقطع...")

    # التحقق إذا كان الرابط من إنستغرام
    is_insta = "instagram.com" in url
    
    try:
        # إذا كان إنستا، سنحاول التحميل مباشرة لتقليل الطلبات
        if is_insta:
            path = f"downloads/insta_{int(time.time())}.mp4"
            opts = INSTA_OPTS.copy()
            opts['outtmpl'] = path
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await run_sync(ydl.extract_info, url, True)
                
            attr = [DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
            
            await ABH.send_file(e.chat_id, path, caption="✅ تم تحميل مقطع إنستغرام", attributes=attr)
            await status.delete()
            if os.path.exists(path): os.remove(path)
            
        else:
            # معالجة يوتيوب والمنصات الأخرى (كما في الكود السابق)
            # ... (يمكنك وضع كود يوتيوب هنا)
            await status.edit("هذا الرابط ليس من إنستغرام، يرجى إرسال رابط فيديو.")

    except Exception as ex:
        error_msg = str(ex)
        if "401" in error_msg or "Login required" in error_msg:
            await status.edit("⚠️ إنستغرام يطلب تسجيل دخول (كوكيز) لهذا الرابط، لا يمكن تخطيه حالياً بدونها.")
        else:
            await status.edit(f"⚠️ فشل التحميل:\n`{error_msg[:100]}`")
