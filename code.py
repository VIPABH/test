import asyncio, yt_dlp, os, re, uuid, json, shutil
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r 

# --- 1. الدوال المساعدة ---
async def run_sync(func, *args):
    """تشغيل المهام الثقيلة في Thread منفصل لضمان عدم توقف البوت"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def extract_data(text):
    # نمط يوتيوب
    yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|shorts/|)([0-9A-Za-z_-]{11}))', text)
    # نمط إنستقرام (بوست، ريلز، TV)
    ig = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+))', text)
    # نمط تيك توك (الروابط العادية والمختصرة)
    tt = re.search(r'(https?://(?:www\.|vm\.|vt\.)?tiktok\.com/.*)', text)

    if yt: return "youtube", yt.group(1), yt.group(2)
    if ig: return "instagram", ig.group(1), ig.group(2)
    if tt: return "tiktok", tt.group(1), "tiktok_video"
    return None, None, None

# --- 2. معالج الرسائل ---
@ABH.on(events.NewMessage(incoming=True))
async def handler(e):
    if not e.is_private or not e.text: return
    p, url, vid = extract_data(e.text.strip())
    
    if p:
        sid = str(uuid.uuid4())[:8]
        r.setex(f"tmp:{sid}", 600, json.dumps({"u": url, "v": vid, "p": p, "id": e.sender_id}))
        btns = [[Button.inline("🎥 فيديو (MP4)", data=f"v|{sid}"), Button.inline("🎵 صوت (MP3)", data=f"a|{sid}")]]
        await e.reply(f"**✅ تم كشف رابط {p.upper()}**\nاختر النوع للبدء بعملية مستقلة:", buttons=btns)
    elif not e.text.startswith('/'):
        res = await run_sync(lambda: Y88F8(e.text, max_results=5).to_dict())
        msg = "\n".join([f"• **{r['title']}**\n🔗 `https://youtu.be/{r['id']}`" for r in res])
        await e.reply(msg or "❌ لا توجد نتائج.", link_preview=False)

# --- 3. محرك التحميل المستقل ---
@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def dl_callback(e):
    data_raw = r.get(f"tmp:{e.data.decode().split('|')[1]}")
    if not data_raw: return await e.answer("⚠️ الطلب انتهى.")
    
    data = json.loads(data_raw)
    if data['id'] != e.sender_id: return await e.answer("⚠️ هذا الطلب ليس لك.")
    
    type_dl = e.data.decode().split('|')[0]
    asyncio.create_task(process_download(e, data, type_dl))

async def process_download(event, data, type_dl):
    uid = uuid.uuid4().hex
    task_dir = f"downloads/{uid}"
    os.makedirs(task_dir, exist_ok=True)
    file_path = f"{task_dir}/media"

    await event.edit(f"⏳ جاري معالجة رابط {data['p']}...")

    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
        # إضافة Headers لتجنب الحظر من انستقرام وتيك توك
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if type_dl == 'v':
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_ops["merge_output_format"] = "mp4"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = await run_sync(ydl.extract_info, data['u'], True)
            
        downloaded_file = next((f"{task_dir}/{f}" for f in os.listdir(task_dir) if f.startswith("media")), None)
        if not downloaded_file: raise Exception("لم يتم العثور على الملف المحمل")

        title = info.get('title', 'بدون عنوان')
        duration = int(info.get('duration', 0))

        if type_dl == 'v':
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"✅ **{data['p'].capitalize()} Downloaded**\n🎬 `{title}`",
                attributes=[DocumentAttributeVideo(
                    duration=duration,
                    w=info.get('width', 0), h=info.get('height', 0),
                    supports_streaming=True
                )],
                force_document=False
            )
        else:
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"🎵 **Audio:** `{title}`",
                attributes=[DocumentAttributeAudio(duration=duration, title=title)]
            )
        
        await event.delete()

    except Exception as ex:
        await event.edit(f"❌ خطأ: {str(ex)[:100]}")
    
    finally:
        await run_sync(lambda: shutil.rmtree(task_dir, ignore_errors=True))

print("✅ البوت يدعم الآن: YouTube, Instagram, TikTok")
