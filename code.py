import yt_dlp
import os
import asyncio
import time
import uuid
import math
import glob
from ABH import *
from telethon import events
from telethon.tl.functions.upload import SaveBigFilePartRequest
from telethon.tl.types import DocumentAttributeVideo, InputFileBig

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)

# 🚀 دالة الرفع النفاث (40 اتصال + قطعة 1.5MB)
async def fast_upload(client, file_path, connections=40):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    part_size = 1536 * 1024 
    part_count = math.ceil(file_size / part_size)
    
    with open(file_path, 'rb') as f:
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                tasks.append(client(SaveBigFilePartRequest(file_id, j, part_count, chunk)))
            if tasks: await asyncio.gather(*tasks)
            
    return InputFileBig(file_id, part_count, os.path.basename(file_path))

# 🛠 إعدادات محاكاة التطبيقات (تجاوز 403 بدون كوكيز)
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 20,
    # السر هنا: إجبار اليوتيوب على رؤية الطلب كأنه من تطبيق أندرويد
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios'],
            'player_skip': ['webpage', 'configs']
        }
    },
    'user_agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)',
}

@ABH.on(events.NewMessage)
async def vps_2sec_target_handler(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot): return

    start_all = time.time()
    url = e.text.strip()
    status = await e.reply("📡 **محاكاة تطبيق YouTube...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        template = os.path.join(DOWNLOAD_DIR, f"v_{u_id}.%(ext)s")
        
        # --- التحميل الذكي ---
        check_start = time.time()
        with yt_dlp.YoutubeDL({**YDL_OPTS, 'outtmpl': template}) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if 'entries' in info: info = info['entries'][0]

        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"v_{u_id}.*"))
        if not files: raise Exception("فشل في العثور على الملف")
        actual_path = files[0] 
        
        dl_time = round(time.time() - check_start, 2)

        # --- الرفع الصاروخي ---
        await status.edit(f"📤 **رفع نفاث (Turbo)...**")
        up_start = time.time()
        fast_file = await fast_upload(ABH, actual_path, connections=40)
        up_time = round(time.time() - up_start, 2)
        
        # --- الإرسال النهائي ---
        await ABH.send_file(
            e.chat_id, fast_file,
            caption=(
                f"✅ **تم التحميل بنمط التطبيق**\n\n"
                f"📥 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{up_time}s`\n"
                f"🚀 **الإجمالي:** `{round(time.time() - start_all, 2)}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280), h=info.get('height', 720),
                supports_streaming=True
            )],
            supports_streaming=True, use_cache=False
        )

        await status.delete()
        if os.path.exists(actual_path): os.remove(actual_path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:**\n`{str(ex)[:150]}`")
