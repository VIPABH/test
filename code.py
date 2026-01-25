import asyncio, yt_dlp, os, re, uuid, json, shutil
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r 

# --- 1. الدوال المساعدة ---
async def run_sync(func, *args):
    """تشغيل المهام الثقيلة في Thread منفصل لضمان عدم توقف البوت"""
    loop = asyncio.get_event_loop()
    # نستخدم lambda هنا لتغليف الدالة إذا كانت تحتوي على وسائط معقدة
    return await loop.run_in_executor(None, func, *args)

def extract_data(text):
    yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|shorts/|)([0-9A-Za-z_-]{11}))', text)
    ig = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+))', text)
    if yt: return "youtube", yt.group(1), yt.group(2)
    if ig: return "instagram", ig.group(1), ig.group(2)
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
        # البحث يعمل بشكل مستقل لمنع تجميد البوت
        res = await run_sync(lambda: Y88F8(e.text, max_results=5).to_dict())
        msg = "\n".join([f"• **{r['title']}**\n🔗 `https://youtu.be/{r['id']}`" for r in res])
        await e.reply(msg or "❌ لا توجد نتائج.", link_preview=False)

# --- 3. محرك التحميل المستقل (Concurrency Logic) ---
@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def dl_callback(e):
    data_raw = r.get(f"tmp:{e.data.decode().split('|')[1]}")
    if not data_raw: return await e.answer("⚠️ الطلب انتهى.")
    
    data = json.loads(data_raw)
    if data['id'] != e.sender_id: return await e.answer("⚠️ هذا الطلب ليس لك.")
    
    type_dl = e.data.decode().split('|')[0]
    # إنشاء مهمة asyncio مستقلة تماماً لهذه العملية
    asyncio.create_task(process_download(e, data, type_dl))

async def process_download(event, data, type_dl):
    """دالة المعالجة المستقلة لكل مستخدم"""
    uid = uuid.uuid4().hex
    task_dir = f"downloads/{uid}"
    os.makedirs(task_dir, exist_ok=True)
    file_path = f"{task_dir}/media"

    await event.edit("⏳ جاري التحميل... (عملية مستقلة)")

    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
    }

    if type_dl == 'v':
        # طلب أفضل جودة أصلية بصيغة MP4 لضمان عملها كفيديو
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_ops["merge_output_format"] = "mp4"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        # تنفيذ التحميل
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = await run_sync(ydl.extract_info, data['u'], True)
            
        # العثور على الملف المحمل في المجلد الخاص بالمهمة
        downloaded_file = next((f"{task_dir}/{f}" for f in os.listdir(task_dir) if f.startswith("media")), None)
        
        if not downloaded_file: raise Exception("File not found")

        # إرسال الملف كفيديو أو صوت
        if type_dl == 'v':
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"✅ **تم التحميل بنجاح**\n🎬 `{info['title']}`",
                attributes=[DocumentAttributeVideo(
                    duration=int(info.get('duration', 0)),
                    w=info.get('width', 0), h=info.get('height', 0),
                    supports_streaming=True
                )],
                force_document=False
            )
        else:
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"🎵 **صوت:** `{info['title']}`",
                attributes=[DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'))]
            )
        
        await event.delete()

    except Exception as ex:
        await event.edit(f"❌ خطأ: {str(ex)[:100]}")
    
    finally:
        # حل مشكلة TypeError: نمرر الدالة بدون Keyword Arguments
        # نستخدم lambda للالتفاف على ignore_errors داخل executor
        await run_sync(lambda: shutil.rmtree(task_dir, ignore_errors=True))

# --- تشغيل البوت ---
print("✅ البوت يعمل بنظام asyncio المستقل تماماً...")
