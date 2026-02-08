import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# التأكد من المجلد
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

# إعدادات متوافقة مع الـ VPS وسريعة جداً
OPTS = {
    # تحميل أفضل جودة فيديو mp4 وأفضل صوت m4a لضمان سرعة الدمج
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'concurrent_fragment_downloads': 10,
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
    'http_headers': {'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)'},
}

import yt_dlp
import os
import asyncio
import time
import uuid
# تأكد من تثبيت مكتبة telethon_ext_fast_upload إذا أردت أداءً خارقاً
# أو سنعتمد على تحسين تدفق البيانات المباشر
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# ... (إعدادات التحميل نفسها كما في الكود السابق)

@ABH.on(events.NewMessage)
async def vps_turbo_uploader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    received_at = time.time()
    latency = round(received_at - e.date.timestamp(), 2)
    url = e.text.strip()
    status = await e.reply("📡 **جاري المعالجة...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path_no_ext = os.path.join("downloads", f"v_{u_id}")
        
        # --- مرحلة الفحص والتحميل (مختصرة للتركيز على الرفع) ---
        check_start = time.time()
        with yt_dlp.YoutubeDL(OPTS) as ydl:
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=True))
            if 'entries' in info: info = info['entries'][0]
        
        check_time = round(time.time() - check_start, 2)
        actual_file = f"{path_no_ext}.mp4" # افترضنا mp4 للتبسيط
        
        # --- مرحلة الرفع السريع (Turbo Upload) ---
        await status.edit(f"📤 **جاري الرفع الصاروخي...**")
        up_start = time.time()

        # تحسين الرفع عبر استخدام حجم بافر كبير وتقليل استهلاك المعالج
        with open(actual_file, 'rb') as f:
            # استخدام send_file مع تفضيل سرعة التدفق
            # ملاحظة: بعض السيرفرات تحتاج لوجود MTProto Proxy لزيادة سرعة الرفع
            video = await ABH.send_file(
                e.chat_id,
                f,
                caption=(
                    f"✅ **تمت العملية بنجاح**\n"
                    f"📡 الاستلام: `{latency}s`\n"
                    f"🔍 الفحص: `{check_time}s`\n"
                    f"📤 الرفع: `{round(time.time() - up_start, 2)}s`\n"
                    f"🚀 الإجمالي: `{round(time.time() - received_at, 2)}s`"
                ),
                attributes=[DocumentAttributeVideo(
                    duration=int(info.get('duration', 0)),
                    w=info.get('width', 1280), h=info.get('height', 720),
                    supports_streaming=True
                )],
                # هذه الخاصية تجعل تيليجرام يبدأ المعالجة فورياً
                part_size_kb=512 # زيادة حجم القطعة المرفوعة لسرعة أكبر
            )

        await status.delete()
        if os.path.exists(actual_file): os.remove(actual_file)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:150]}`")
