import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# إعدادات VPS القصوى بدون aria2c (لتجنب 403)
VPS_EXTREME_OPTS = {
    # دمج الفيديو والصوت بأعلى جودة mp4
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    
    # السرعة البديلة لـ aria2c (التحميل المتوازي الداخلي)
    'concurrent_fragment_downloads': 15, 
    
    # تجاوز حظر يوتيوب عبر محاكاة الأندرويد
    'extractor_args': {
        'youtube': {
            'player_client': ['android_test', 'ios'],
            'player_skip': ['webpage']
        }
    },
    
    # رؤوس الطلب لضمان عدم حدوث 403
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    
    'buffersize': 1024 * 1024 * 16, # 16MB
}

@ABH.on(events.NewMessage)
async def vps_fix_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🛡️ **جاري التحميل بنظام تجاوز القيود...**")
    start_time = time.time()

    try:
        u_id = uuid.uuid4().hex[:6]
        path = f"downloads/vps_{u_id}.mp4"
        
        opts = VPS_EXTREME_OPTS.copy()
        opts['outtmpl'] = path

        # التحميل
        with yt_dlp.YoutubeDL(opts) as ydl:
            # هنا نقوم بالتحميل مباشرة
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        dl_time = round(time.time() - start_time, 2)
        await status.edit(f"📥 **اكتمل التحميل:** `{dl_time}s`\n🚀 **جاري الرفع...**")

        # الرفع
        up_start = time.time()
        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **تم التحميل بنجاح (Bypass Mode)**\n"
                f"⏱ التحميل: `{dl_time}s`\n"
                f"🚀 الإجمالي: `{round(time.time() - start_time, 2)}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
        )
        
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل التحميل:**\n`يوتيوب يرفض الطلب (403). جرب رابطاً آخر أو انتظر قليلاً.`")
        print(f"Error: {str(ex)}")
