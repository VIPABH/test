import yt_dlp
import os
import asyncio
import time
import uuid
import math
import io
from ABH import *
from telethon import events
from telethon.tl.functions.upload import SaveBigFilePartRequest
from telethon.tl.types import DocumentAttributeVideo, InputFileBig

# إعدادات المحاكاة (تطبيق أندرويد)
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {'youtube': {'player_client': ['android'], 'player_skip': ['webpage']}},
}

@ABH.on(events.NewMessage)
async def streaming_handler(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot): return

    start_all = time.time()
    url = e.text.strip()
    status = await e.reply("⚡ **وضع التدفق النفاث (Streaming)...**")
    
    try:
        # 1. استخراج معلومات الفيديو أولاً (بسرعة)
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            file_size = info.get('filesize_approx') or info.get('filesize') or 0
            
        file_id = uuid.uuid4().int & (1 << 63) - 1
        part_size = 512 * 1024
        part_count = math.ceil(file_size / part_size) if file_size else 0
        
        # 2. بدء التحميل والرفع في نفس اللحظة
        # سنستخدم "Generator" لسحب البيانات ورفعها مباشرة
        up_start = time.time()
        current_part = 0
        
        def download_and_upload():
            nonlocal current_part
            # خيارات استخراج البيانات كـ Stream
            ydl_stream_opts = {**YDL_OPTS, 'outtmpl': '-'} # الرمز '-' يعني الإخراج للذاكرة
            
            with yt_dlp.YoutubeDL(ydl_stream_opts) as ydl_s:
                # سحب الفيديو كـ Generator
                for chunk in ydl_s.download_iter([url]):
                    if chunk['status'] == 'downloading' and 'data' in chunk:
                        # هنا نرفع القطعة فور استلامها
                        data = chunk['data']
                        # ملاحظة: قد تحتاج لتقسيم الداتا لقطع 512KB إذا كانت أكبر
                        # هذا مثال مبسط للمفهوم
                        pass

        # لتطبيق هذا بفعالية قصوى، سنستخدم مكتبة تهتم بالـ Pipe
        # إليك الطريقة الأسرع باستخدام "fast_upload" معدلة تعمل مع Buffer
        
        await status.edit("🚀 **جاري الضخ المتوازي...**")

        # [توضيح] نظام الـ Streaming الحقيقي يحتاج لتعامل مع stdout
        # لكن للتبسيط والسرعة، سنشغل الرفع في Task منفصلة تبدأ بمجرد وجود أول 1MB
        
        # دعنا نطبق "الخديعة" البرمجية الأسرع:
        # تشغيل الرفع المتوازي فور بدء التحميل (Multithreading)
        
        path = f"downloads/{uuid.uuid4().hex}.mp4"
        
        # تشغيل التحميل في الخلفية
        dl_task = asyncio.get_event_loop().run_in_executor(None, lambda: os.system(f'yt-dlp "{url}" -o "{path}" --quiet'))
        
        # انتظار وجود أول 1MB فقط
        while not os.path.exists(path) or os.path.getsize(path) < 1024 * 1024:
            await asyncio.sleep(0.2)
            if time.time() - start_all > 10: break # حماية من التعليق

        # الرفع يبدأ والملف لا يزال يُحمل!
        fast_file = await fast_upload_async(ABH, path, file_size)
        
        await ABH.send_file(e.chat_id, fast_file, caption=f"🚀 الإجمالي: {round(time.time()-start_all, 2)}s", supports_streaming=True)
        
    except Exception as ex:
        await status.edit(f"⚠️ فشل: {str(ex)}")

async def fast_upload_async(client, path, total_size):
    # دالة رفع ذكية تراقب حجم الملف أثناء نموه
    file_id = uuid.uuid4().int & (1 << 63) - 1
    part_size = 512 * 1024
    current_offset = 0
    part_index = 0
    tasks = []
    
    while True:
        if os.path.exists(path):
            current_size = os.path.getsize(path)
            if current_size > current_offset + part_size:
                with open(path, 'rb') as f:
                    f.seek(current_offset)
                    chunk = f.read(part_size)
                    tasks.append(client(SaveBigFilePartRequest(file_id, part_index, 1000, chunk))) # 1000 قيمة افتراضية للـ count
                    current_offset += part_size
                    part_index += 1
            elif current_size >= total_size and total_size != 0:
                break # انتهى التحميل والرفع
        await asyncio.sleep(0.1)
    
    await asyncio.gather(*tasks)
    return InputFileBig(file_id, part_index, "video.mp4")
