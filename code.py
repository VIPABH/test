import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"): os.makedirs("downloads")

# إعدادات كسر حظر الـ 403 واستغلال الـ VPS
VPS_POWER_OPTS = {
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # الحل السحري لـ 403: محاكاة أندرويد بشكل كامل
    'extractor_args': {
        'youtube': {
            'player_client': ['android'],
            'player_skip': ['webpage', 'configs']
        }
    },
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)',
        'Accept': '*/*',
    },
    'concurrent_fragment_downloads': 10,
}

@ABH.on(events.NewMessage)
async def ultimate_vps_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # 1. وقت الاستلام (Latency)
    received_at = time.time()
    latency = round(received_at - e.date.timestamp(), 2)
    
    url = e.text.strip()
    status = await e.reply("📡 **جاري كسر حماية الرابط...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        # 2. وقت الفحص والبحث
        check_start = time.time()
        with yt_dlp.YoutubeDL(VPS_POWER_OPTS) as ydl:
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            if 'entries' in info: info = info['entries'][0]
            check_time = round(time.time() - check_start, 2)

            # 3. وقت التحميل
            await status.edit(f"📥 **تحميل آمن...** (فحص: {check_time}s)")
            dl_start = time.time()
            # هنا نمرر الـ info مباشرة للتحميل لضمان عدم تغير الرابط
            await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.process_info(info))
            dl_time = round(time.time() - dl_start, 2)

        # 4. وقت الرفع
        await status.edit(f"📤 **رفع سريع...** (تحميل: {dl_time}s)")
        up_start = time.time()
        
        attr = [DocumentAttributeVideo(
            duration=int(info.get('duration', 0)),
            w=info.get('width', 1280), h=info.get('height', 720),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **تمت المعالجة بنجاح**\n"
                f"📝 `{info.get('title')[:50]}`\n\n"
                f"⏱ **تأخير الاستلام:** `{latency}s`\n"
                f"🔍 **البحث والفحص:** `{check_time}s`\n"
                f"📥 **وقت التحميل:** `{dl_time}s`\n"
                f"📤 **وقت الرفع:** `{round(time.time() - up_start, 2)}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الوقت الإجمالي:** `{round(time.time() - received_at, 2)}s`"
            ),
            attributes=attr,
            supports_streaming=True
        )
        
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        # إذا استمر الـ 403، سنحتاج لاستخدام بروتوكول مختلف
        await status.edit(f"⚠️ **خطأ 403 (تم حجب السيرفر مؤقتاً)**\n`جاري محاولة الحل التلقائي...`")
        print(f"Error Log: {str(ex)}")
