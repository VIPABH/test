import yt_dlp
import os
import asyncio
import time
import uuid
import math
from ABH import *
from telethon import events, utils
from telethon.tl.types import DocumentAttributeVideo, InputFile

if not os.path.exists("downloads"): os.makedirs("downloads")

# دالة الرفع المتوازي - تفتح 16 اتصالاً في آن واحد
async def fast_upload(client, file_path, connections=16):
    file_id = uuid.uuid4().int & (1 << 63) - 1
    file_size = os.path.getsize(file_path)
    # حجم القطعة 512KB هو الأفضل للسرعات العالية
    part_size = 512 * 1024
    part_count = math.ceil(file_size / part_size)
    
    with open(file_path, 'rb') as f:
        for i in range(0, part_count, connections):
            tasks = []
            for j in range(i, min(i + connections, part_count)):
                offset = j * part_size
                f.seek(offset)
                chunk = f.read(part_size)
                # رفع القطع بالتوازي
                tasks.append(client(utils.get_query(
                    InputFile(file_id, part_count, f'v_{file_id}.mp4', md5_checksum=''),
                    chunk, j
                )))
            await asyncio.gather(*tasks)
            
    return InputFile(file_id, part_count, os.path.basename(file_path), '')

@ABH.on(events.NewMessage)
async def god_speed_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return

    received_at = time.time()
    url = e.text.strip()
    status = await e.reply("📡 **جاري سحب الفيديو...**")
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        # 1. مرحلة التحميل (التي أصبحت سريعة عندك)
        check_start = time.time()
        opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': path,
            'quiet': True,
            'concurrent_fragment_downloads': 15,
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            if 'entries' in info: info = info['entries'][0]
        
        dl_time = round(time.time() - check_start, 2)
        
        # 2. مرحلة الرفع المتوازي (النفاثة)
        await status.edit(f"📥 تحميل: `{dl_time}s`\n🚀 **رفع متوازي بـ 16 اتصال...**")
        up_start = time.time()
        
        # استخدام الدالة السريعة للرفع
        fast_file = await fast_upload(ABH, path)
        
        await ABH.send_file(
            e.chat_id,
            fast_file,
            caption=(
                f"✅ **اكتملت العملية بنجاح**\n\n"
                f"📡 الاستلام: `{round(time.time() - e.date.timestamp(), 2)}s`\n"
                f"📥 التحميل: `{dl_time}s`\n"
                f"📤 الرفع: `{round(time.time() - up_start, 2)}s`\n"
                f"🚀 الإجمالي: `{round(time.time() - received_at, 2)}s`"
            ),
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 1280), h=info.get('height', 720),
                supports_streaming=True
            )]
        )

        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ خطأ: `{str(ex)[:150]}`")
