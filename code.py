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

# 🚀 دالة الرفع المتوازي (Turbo VPS)
async def fast_upload(client, file_path, connections=10):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    part_size = 512 * 1024  # حجم القطعة 512 كيلوبايت
    part_count = math.ceil(file_size / part_size)
    
    with open(file_path, 'rb') as f:
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                # استخدام طلب الملفات الكبيرة دائماً لضمان استلام الجزء 0 بنجاح
                tasks.append(client(SaveBigFilePartRequest(file_id, j, part_count, chunk)))
            
            await asyncio.gather(*tasks)
            
    return InputFileBig(file_id, part_count, os.path.basename(file_path))

# 🛠 إعدادات التحميل القصوى
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 15,
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'},
}

@ABH.on(events.NewMessage)
async def vps_speed_master(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # 1. حساب وقت استلام الأمر (Latency)
    start_all = time.time()
    latency = round(start_all - e.date.timestamp(), 2)
    
    url = e.text.strip()
    status = await e.reply("📡 **بدء المعالجة الذكية...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = os.path.join(DOWNLOAD_DIR, f"v_{u_id}.mp4")
        
        # 2. وقت الفحص والبحث (Info Extraction)
        check_start = time.time()
        search_url = url if url.startswith('http') else f"ytsearch1:{url}"
        
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            if 'entries' in info: info = info['entries'][0]
            check_time = round(time.time() - check_start, 2)

            # 3. وقت التحميل الفعلي (Download Time)
            await status.edit(f"📥 **تحميل:** `فحص: {check_time}s`")
            dl_start = time.time()
            local_opts = YDL_OPTS.copy()
            local_opts['outtmpl'] = path
            
            with yt_dlp.YoutubeDL(local_opts) as ydl_dl:
                await asyncio.get_event_loop().run_in_executor(None, lambda: ydl_dl.process_info(info))
            dl_time = round(time.time() - dl_start, 2)

        # 4. وقت الرفع المتوازي (Upload Time)
        await status.edit(f"📤 **رفع:** `تحميل: {dl_time}s`")
        up_start = time.time()
        
        fast_file = await fast_upload(ABH, path)
        up_time = round(time.time() - up_start, 2)
        
        # 5. الإرسال النهائي وحساب الإجمالي
        await ABH.send_file(
            e.chat_id,
            fast_file,
            caption=(
                f"✅ **تمت العملية بنجاح**\n"
                f"📝 `{info.get('title')[:50]}...`\n\n"
                f"📡 **الاستلام:** `{latency}s`\n"
                f"🔍 **الفحص:** `{check_time}s`\n"
                f"📥 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{up_time}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الإجمالي:** `{round(time.time() - start_all, 2)}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280), h=info.get('height', 720),
                supports_streaming=True
            )],
            supports_streaming=True
        )

        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:** `{str(ex)[:150]}`")
        if 'path' in locals() and os.path.exists(path): os.remove(path)
