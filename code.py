import yt_dlp
import os
import asyncio
import time
import uuid
import math
from ABH import *
from telethon import events, utils
from telethon.tl.types import DocumentAttributeVideo, InputFileUploadSafe

# المجلد المخصص للتحميل
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR): 
    os.makedirs(DOWNLOAD_DIR)

# 🚀 دالة الرفع المتوازي لكسر بطء تيليجرام
async def fast_upload(client, file_path, connections=16):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    part_size = 512 * 1024  # 512KB للقطعة الواحدة
    part_count = math.ceil(file_size / part_size)
    
    # تحديد إذا كان الملف كبير أم صغير في نظام تيليجرام
    is_large = file_size > 10 * 1024 * 1024
    
    with open(file_path, 'rb') as f:
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                
                # إرسال القطعة الواحدة
                if is_large:
                    query = utils.get_query(InputFileUploadSafe(file_id, part_count, 'video.mp4'), chunk, j)
                else:
                    query = utils.get_query(InputFileUploadSafe(file_id, part_count, 'video.mp4'), chunk, j)
                
                tasks.append(client(query))
            
            await asyncio.gather(*tasks)
            
    return InputFileUploadSafe(file_id, part_count, os.path.basename(file_path))

# 🛠 إعدادات التحميل لكسر حظر 403
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'concurrent_fragment_downloads': 15, # تحميل 15 جزء من الفيديو بنفس الوقت
    'extractor_args': {
        'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}
    },
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 14; en_US; Pixel 8 Pro)',
    },
}

@ABH.on(events.NewMessage)
async def ultimate_vps_handler(e):
    # تجاهل الأوامر والرسائل من البوتات
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # 1. توقيت الاستلام
    received_at = time.time()
    latency = round(received_at - e.date.timestamp(), 2)
    
    url = e.text.strip()
    status = await e.reply("📡 **بدء المعالجة النفاثة...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = os.path.join(DOWNLOAD_DIR, f"v_{u_id}.mp4")
        
        # 2. توقيت البحث والتحميل
        check_start = time.time()
        local_opts = YDL_OPTS.copy()
        local_opts['outtmpl'] = path

        with yt_dlp.YoutubeDL(local_opts) as ydl:
            # البحث إذا لم يكن الرابط يبدأ بـ http
            search_url = url if url.startswith('http') else f"ytsearch1:{url}"
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(search_url, download=True))
            if 'entries' in info: info = info['entries'][0]
        
        dl_time = round(time.time() - check_start, 2)

        # 3. توقيت الرفع المتوازي
        await status.edit(f"📥 تحميل: `{dl_time}s`\n🚀 **رفع متوازي (16 اتصال)...**")
        up_start = time.time()
        
        # تنفيذ الرفع المتوازي
        fast_file = await fast_upload(ABH, path)
        
        # إرسال الملف النهائي
        await ABH.send_file(
            e.chat_id,
            fast_file,
            caption=(
                f"✅ **اكتملت العملية بنجاح**\n"
                f"📝 `{info.get('title')[:50]}...`\n\n"
                f"📡 **الاستلام:** `{latency}s`\n"
                f"🔍 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{round(time.time() - up_start, 2)}s`\n"
                f"━━━━━━━━━━━━━━\n"
                f"🚀 **الإجمالي:** `{round(time.time() - received_at, 2)}s`"
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
