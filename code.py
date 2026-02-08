import yt_dlp
import os
import asyncio
import time
import uuid
import math
from ABH import *
from telethon import events
from telethon.tl.functions.upload import SaveBigFilePartRequest
from telethon.tl.types import DocumentAttributeVideo, InputFileBig

# المجلد المخصص للتحميل
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): 
    os.makedirs(DOWNLOAD_DIR)

# 🚀 دالة الرفع المتوازي (المستقرة للملفات الكبيرة)
async def fast_upload(client, file_path, connections=10):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    # استخدام حجم قطعة 512KB
    part_size = 512 * 1024 
    part_count = math.ceil(file_size / part_size)
    
    with open(file_path, 'rb') as f:
        # رفع الأجزاء في مجموعات لضمان عدم ضياع الجزء 0
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                # نستخدم SaveBigFilePartRequest لضمان التوافق مع الملفات الكبيرة والصغيرة
                tasks.append(client(SaveBigFilePartRequest(file_id, j, part_count, chunk)))
            
            await asyncio.gather(*tasks)
            
    # نستخدم InputFileBig لحل مشكلة Part 0 missing بشكل جذري
    return InputFileBig(file_id, part_count, os.path.basename(file_path))

# 🛠 إعدادات التحميل (تجاوز حظر 403)
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 15,
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'},
}

@ABH.on(events.NewMessage)
async def vps_fix_handler(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    received_at = time.time()
    url = e.text.strip()
    status = await e.reply("📡 **جاري التحميل والمعالجة...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = os.path.join(DOWNLOAD_DIR, f"v_{u_id}.mp4")
        
        # --- التحميل ---
        check_start = time.time()
        local_opts = YDL_OPTS.copy()
        local_opts['outtmpl'] = path

        with yt_dlp.YoutubeDL(local_opts) as ydl:
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=True))
            if 'entries' in info: info = info['entries'][0]
        
        dl_time = round(time.time() - check_start, 2)

        # --- الرفع ---
        await status.edit(f"📥 تحميل: `{dl_time}s`\n🚀 **رفع متوازي (Turbo Mode)...**")
        up_start = time.time()
        
        # تنفيذ الرفع المتوازي باستخدام InputFileBig
        fast_file = await fast_upload(ABH, path)
        
        await ABH.send_file(
            e.chat_id,
            fast_file,
            caption=(
                f"✅ **اكتملت العملية**\n"
                f"📝 `{info.get('title')[:50]}...`\n\n"
                f"📥 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{round(time.time() - up_start, 2)}s`\n"
                f"🚀 **الإجمالي:** `{round(time.time() - received_at, 2)}s`"
            ),
            # attributes=[DocumentAttributeVideo(
            #     duration=int(info.get('duration', 0)),
            #     w=info.get('width', 1280), h=info.get('height', 720),
            #     supports_streaming=True
            # )],
            # supports_streaming=True
        )

        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:** `{str(ex)[:150]}`")
        if 'path' in locals() and os.path.exists(path): os.remove(path)
