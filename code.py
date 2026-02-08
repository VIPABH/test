import yt_dlp
import os
import asyncio
import time
import uuid
import sys
from ABH import *
from telethon import events
from telethon.tl.types import DocumentAttributeVideo

# محاولة رفع قيود النظام برمجياً (للسيرفرات القوية فقط)
try:
    import resource
    # رفع حد الملفات المفتوحة لـ 65 ألف لضمان عدم الاختناق
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
except:
    pass

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# إعدادات إجبار الموارد (Resource Enforcement)
ULTRA_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    
    # إجبار استخدام المشغل الذي لا يُخنق حالياً
    'extractor_args': {
        'youtube': {'player_client': ['android_test'], 'player_skip': ['webpage']}
    },
    
    'external_downloader': 'aria2c',
    'external_downloader_args': [
        '--max-connection-per-server=16',
        '--split=16',
        '--min-split-size=100K',
        '--max-overall-download-limit=0',
        '--file-allocation=none',
        '--no-conf', # تجاهل أي إعدادات سابقة للسيرفر قد تقيد السرعة
        '--disable-ipv6=true', # أحياناً الـ IPv6 يسبب بطء شديد في السيرفرات
    ],
    # استخدام بافر ضخم في الرام (Buffer) لتقليل الضغط على الهارد ديسك
    'buffersize': 1024 * 1024 * 32, # 32 ميجا بافر
}

@ABH.on(events.NewMessage)
async def high_priority_downloader(e):
    if not e.text or e.text.startswith(('/', '!', '.')) or (e.sender and e.sender.bot):
        return
    
    url = e.text.strip()
    status = await e.reply("🔥 **إعطاء الأولوية القصوى للموارد...**")
    
    start_time = time.time()
    
    try:
        u_id = uuid.uuid4().hex[:5]
        path = f"downloads/v_{u_id}.mp4"
        
        opts = ULTRA_OPTS.copy()
        opts['outtmpl'] = path

        # تنفيذ العملية في خيط منفصل مع أولوية عالية
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(url, download=True))

        dl_time = round(time.time() - start_time, 2)
        
        await status.edit(f"🚀 **اكتمل التحميل:** `{dl_time}s`\n📤 **جاري الرفع...**")

        await ABH.send_file(
            e.chat_id, path,
            caption=f"✅ **تم استغلال الموارد بنجاح**\n⏱ التحميل: `{dl_time}s`",
            attributes=[DocumentAttributeVideo(
                duration=int(info.get('duration', 0)),
                w=info.get('width', 720), h=info.get('height', 1280),
                supports_streaming=True
            )]
        )
        await status.delete()
        if os.path.exists(path): os.remove(path)

    except Exception as ex:
        await status.edit(f"⚠️ فشل: `{str(ex)[:100]}`")
