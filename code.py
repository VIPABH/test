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

# 🚀 دالة الرفع المتوازي (Extreme Speed Edition)
async def fast_upload(client, file_path, connections=40):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    
    # قطعة ضخمة (1.5MB) لتقليل عدد الطلبات (Requests) وتجاوز الـ Latency
    part_size = 1536 * 1024 
    part_count = math.ceil(file_size / part_size)
    
    with open(file_path, 'rb') as f:
        # تقسيم العمل لرفع 40 قطعة في اللحظة الواحدة
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                # إرسال مباشر للأجزاء الكبيرة لتيليجرام
                tasks.append(client(SaveBigFilePartRequest(file_id, j, part_count, chunk)))
            
            if tasks:
                await asyncio.gather(*tasks)
            
    return InputFileBig(file_id, part_count, os.path.basename(file_path))

# 🛠 إعدادات التحميل القصوى (بدون فحص زائد)
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'concurrent_fragment_downloads': 20, # رفع سرعة سحب الفيديو من يوتيوب
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
    'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'},
}

@ABH.on(events.NewMessage)
async def vps_2sec_target_handler(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    # توقيت الاستلام الكلي
    start_all = time.time()
    url = e.text.strip()
    status = await e.reply("🚀 **جاري الإطلاق...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = os.path.join(DOWNLOAD_DIR, f"v_{u_id}.mp4")
        
        # --- الفحص والتحميل ---
        check_start = time.time()
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # استخراج المعلومات والتحميل في خطوة واحدة لتقليل الوقت
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if 'entries' in info: info = info['entries'][0]
            # التأكد من المسار الصحيح في حال قام yt-dlp بتغيير الاسم
            if not os.path.exists(path):
                # بحث عن الملف الحقيقي
                potential_files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if u_id in f]
                if potential_files: path = potential_files[0]

        dl_time = round(time.time() - check_start, 2)

        # --- الرفع النفاث ---
        await status.edit(f"📤 **رفع صاروخي...**")
        up_start = time.time()
        
        # استدعاء دالة الـ 40 اتصال
        fast_file = await fast_upload(ABH, path, connections=40)
        up_time = round(time.time() - up_start, 2)
        
        # --- الإرسال الصاروخي ---
        # استخدام attributes لضمان التشغيل كفيديو مباشر دون معالجة إضافية
        await ABH.send_file(
            e.chat_id,
            fast_file,
            caption=(
                f"✅ **تم التحطيم!**\n\n"
                f"📥 **التحميل:** `{dl_time}s`\n"
                f"📤 **الرفع:** `{up_time}s`\n"
                f"🚀 **الإجمالي:** `{round(time.time() - start_all, 2)}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280), h=info.get('height', 720),
                supports_streaming=True
            )],
            supports_streaming=True,
            use_cache=False # لعدم إضاعة الوقت في البحث عن نسخ قديمة
        )

        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ **فشل:** `{str(ex)[:150]}`")
        if 'path' in locals() and os.path.exists(path): os.remove(path)
