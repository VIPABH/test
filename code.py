import asyncio, yt_dlp, os
from telethon import events, Button
from telethon.tl.types import DocumentAttributeAudio
from concurrent.futures import ThreadPoolExecutor
from ABH import ABH 
os.makedirs("downloads", exist_ok=True)
executor = ThreadPoolExecutor(max_workers=10)
YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s", 
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "m4a",
    }],
}
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)
@ABH.on(events.NewMessage(pattern='^(حمل|يوت|تحميل|yt) ?(.*)'))
async def search_handler(e):
    if not e.is_group:return
    query = e.pattern_match.group(2)    
    if not query:
        r = await e.get_reply_message()
        if not r:return await e.reply("اذكر لي اسم المقطع او الرابط")
        query = r.text
    fast_opts = {"quiet": True, "extract_flat": True, "nocheckcertificate": True}
    try:
        with yt_dlp.YoutubeDL(fast_opts) as ydl:
            info = await run_sync(ydl.extract_info, f"ytsearch5:{query}", False)
            results = info.get('entries', [])
        if not results:
            return await e.reply("❌ لم يتم العثور على نتائج!")
        buttons = []
        for video in results:
            title = video.get('title', 'بدون عنوان')
            title = title[:50] + '...' if len(title) > 50 else title
            vid_id = video.get('id')
            buttons.append([Button.inline(title, data=f"yt_{vid_id}")])
        await e.reply(f"• نتائج البحث لـ : **{query}**", buttons=buttons)
    except Exception as ex:
        await e.reply(f"❌ حدث خطأ أثناء البحث: {str(ex)}")
@ABH.on(events.CallbackQuery(pattern=b'^yt_(.*)'))
async def download_callback(e):
    vid_id = e.data.decode().split('_')[1]
    url = f"https://www.youtube.com/watch?v={vid_id}"
    await e.answer("جاري التحميل...", alert=False)
    wait_msg = await e.edit("📥 جاري التحميل، يرجى الانتظار...")
    actual_path = None
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = await run_sync(ydl.extract_info, url, False)
            title = info.get('title', 'Unknown Title')
            duration = int(info.get('duration', 0))
            uploader = info.get('uploader', 'Unknown Artist')
        opts = YDL_OPTS.copy()
        await run_sync(lambda: yt_dlp.YoutubeDL(opts).download([url]))
        actual_path = f"downloads/{vid_id}.m4a"
        if not os.path.exists(actual_path):
            for ext in ['mp3', 'ogg', 'opus', 'webm']:
                test_path = f"downloads/{vid_id}.{ext}"
                if os.path.exists(test_path):
                    actual_path = test_path
                    break
        if not actual_path or not os.path.exists(actual_path):
            raise Exception("اكتمل التحميل ولكن تعذر العثور على الملف.")
        await wait_msg.edit("🚀 جاري الرفع إلى المجموعة...")
        await ABH.send_file(
            e.chat_id,
            file=actual_path, 
            caption=f"**{title}**",
            attributes=[DocumentAttributeAudio(duration=duration, title=title, performer=uploader)]
        )
        await wait_msg.delete()
    except Exception as ex:
        await wait_msg.edit(f"❌ حدث خطأ: {str(ex)}")
    finally:
        if actual_path and os.path.exists(actual_path):
            try:
                os.remove(actual_path)
            except:
                pass
