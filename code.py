import yt_dlp
import os, asyncio, time, uuid, math, glob
from ABH import *
from telethon import events
from telethon.tl.functions.upload import SaveBigFilePartRequest
from telethon.tl.types import DocumentAttributeVideo, InputFileBig

# إعدادات المحاكاة القصوى لتجاوز الـ 403
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
}

@ABH.on(events.NewMessage)
async def fast_stream_handler(e):
    if not e.text or e.text.startswith(('/', '!', '.')): return
    
    start_all = time.time()
    url = e.text.strip()
    msg = await e.reply("🚀 **بدء الضخ المتوازي (2s Target)...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        # 1. جلب معلومات الحجم أولاً (مهم جداً للرفع المتزامن)
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            f_size = info.get('filesize_approx') or info.get('filesize', 0)

        # 2. تشغيل التحميل في الخلفية (Task منفصل)
        def download_proc():
            with yt_dlp.YoutubeDL({**YDL_OPTS, 'outtmpl': path}) as ydl:
                ydl.download([url])

        dl_task = asyncio.get_event_loop().run_in_executor(None, download_proc)

        # 3. الرفع "أثناء" التحميل
        file_id = uuid.uuid4().int & (1 << 63) - 1
        part_size = 512 * 1024
        sent_bytes = 0
        part_index = 0
        tasks = []

        # انتظر حتى يبدأ الملف بالظهور
        while not os.path.exists(path): await asyncio.sleep(0.1)

        while True:
            current_size = os.path.getsize(path)
            # إذا توفرت قطعة جديدة 512KB، ارفعها فوراً
            if current_size >= sent_bytes + part_size:
                with open(path, 'rb') as f:
                    f.seek(sent_bytes)
                    chunk = f.read(part_size)
                    tasks.append(ABH(SaveBigFilePartRequest(file_id, part_index, 3999, chunk))) # 3999 كحد أقصى وهمي
                    sent_bytes += part_size
                    part_index += 1
            
            # التحقق من انتهاء التحميل
            if dl_task.done() and current_size <= sent_bytes:
                # رفع آخر قطعة متبقية (أصغر من 512KB)
                remaining = current_size - sent_bytes
                if remaining > 0:
                    with open(path, 'rb') as f:
                        f.seek(sent_bytes)
                        tasks.append(ABH(SaveBigFilePartRequest(file_id, part_index, part_index + 1, f.read())))
                        part_index += 1
                break
            await asyncio.sleep(0.05) # فحص سريع جداً للبيانات

        await asyncio.gather(*tasks)
        final_file = InputFileBig(file_id, part_index, os.path.basename(path))

        # 4. إرسال الفيديو
        await ABH.send_file(
            e.chat_id, final_file,
            caption=f"✅ **تم التحطيم!**\n🚀 **الإجمالي:** `{round(time.time() - start_all, 2)}s`",
            attributes=[DocumentAttributeVideo(duration=int(info.get('duration', 0)), 
                        w=info.get('width', 1280), h=info.get('height', 720), supports_streaming=True)],
            supports_streaming=True
        )
        await msg.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await msg.edit(f"⚠️ فشل: `{ex}`")
