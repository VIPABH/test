import yt_dlp
import os
import asyncio
import time
import uuid
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات ذكية: تختار الأفضل المتاح وتدمجه تلقائياً
VPS_FLEX_OPTS = {
    # 'bestvideo+bestaudio/best' تضمن عدم حدوث خطأ "Format not available"
    'format': 'bestvideo+bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'merge_output_format': 'mp4', # دمج النتيجة النهائية في mp4 للتيليجرام
    
    # التحميل المتوازي الداخلي (بديل aria2c لتجنب 403)
    'concurrent_fragment_downloads': 10, 
    
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'],
            'player_skip': ['webpage']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    },
}

@ABH.on(events.NewMessage)
async def flexible_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("📡 **جاري جلب الفيديو بأفضل صيغة متاحة...**")
    start_time = time.time()

    try:
        u_id = uuid.uuid4().hex[:6]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = VPS_FLEX_OPTS.copy()
        opts['outtmpl'] = path

        with yt_dlp.YoutubeDL(opts) as ydl:
            # التحميل والدمج التلقائي
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        dl_time = round(time.time() - start_time, 2)
        await status.edit(f"📥 **تم التحميل والدمج:** `{dl_time}s`\n🚀 **جاري الرفع...**")

        # الرفع
        up_start = time.time()
        await ABH.send_file(
            e.chat_id, path,
            caption=(
                f"✅ **تمت المعالجة بنجاح**\n"
                f"⏱ وقت التنفيذ: `{dl_time}s`\n"
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
        error_msg = str(ex)
        await status.edit(f"⚠️ **حدث خطأ:**\n`{error_msg[:150]}`")
