import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"): os.makedirs("downloads")

# إعدادات الأداء الخام فقط
PURE_OPTS = {
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 15,
    'nocheckcertificate': True,
}

@ABH.on(events.NewMessage)
async def speed_radar_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # 1. حساب وقت الاستلام (من إرسالك حتى وصولها للبوت)
    received_at = time.time()
    latency = round(received_at - e.date.timestamp(), 2)
    
    url = e.text.strip()
    status = await e.reply("🚀 **بدء المعالجة...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        # 2. وقت الفحص والبحث (Info Extraction)
        check_start = time.time()
        opts = PURE_OPTS.copy()
        opts['outtmpl'] = path
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            # دمج البحث مع الفحص لربح الوقت
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            if 'entries' in info: info = info['entries'][0]
            check_time = round(time.time() - check_start, 2)

            # 3. وقت التحميل الفعلي
            await status.edit(f"📥 **جاري التحميل...** (فحص: {check_time}s)")
            dl_start = time.time()
            await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.download([info['webpage_url']]))
            dl_time = round(time.time() - dl_start, 2)

        # 4. وقت الرفع
        await status.edit(f"📤 **جاري الرفع...** (تحميل: {dl_time}s)")
        up_start = time.time()
        
        attr = [DocumentAttributeVideo(
            duration=int(info.get('duration', 0)),
            w=info.get('width', 1280), h=info.get('height', 720),
            supports_streaming=True
        )]

        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **اكتملت العملية**\n"
                f"📝 `{info.get('title')[:50]}`\n\n"
                f"📡 **تأخير الاستلام:** `{latency}s`\n"
                f"🔍 **البحث والفحص:** `{check_time}s`\n"
                f"📥 **وقت التحميل:** `{dl_time}s`\n"
                f"📤 **وقت الرفع:** `{round(time.time() - up_start, 2)}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الإجمالي:** `{round(time.time() - received_at, 2)}s`"
            ),
            attributes=attr,
            supports_streaming=True
        )
        
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **خطأ:** `{str(ex)[:100]}`")
