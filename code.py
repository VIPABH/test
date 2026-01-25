import asyncio, yt_dlp, os, re, uuid, json, shutil
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r 

# --- 1. الدوال المساعدة ---
async def run_sync(func, *args):
    """تشغيل المهام الثقيلة في خيط منفصل لمنع تجميد البوت"""
    return await asyncio.get_event_loop().run_in_executor(None, func, *args)

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
        # حفظ بيانات الطلب مع ربطها بمعرف المستخدم لزيادة الأمان
        r.setex(f"tmp:{sid}", 600, json.dumps({"u": url, "v": vid, "p": p, "id": e.sender_id}))
        btns = [[Button.inline("🎥 فيديو (MP4)", data=f"v|{sid}"), Button.inline("🎵 صوت (MP3)", data=f"a|{sid}")]]
        await e.reply(f"**✅ تم كشف رابط {p.upper()}**\nاختر النوع لبدء التحميل المستقل:", buttons=btns)
    elif not e.text.startswith('/'):
        # البحث يعمل بشكل مستقل أيضاً
        res = await run_sync(lambda: Y88F8(e.text, max_results=5).to_dict())
        msg = "\n".join([f"• **{r['title']}**\n🔗 `https://youtu.be/{r['id']}`" for r in res])
        await e.reply(msg or "❌ لا توجد نتائج.")

# --- 3. محرك التحميل المستقل (Task Per Request) ---
@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def dl_callback(e):
    # استخراج البيانات
    callback_data = e.data.decode().split('|')
    type_dl = callback_data[0]
    sid = callback_data[1]
    
    raw = r.get(f"tmp:{sid}")
    if not raw: return await e.answer("⚠️ انتهت صلاحية الطلب.")
    data = json.loads(raw)
    
    if data['id'] != e.sender_id:
        return await e.answer("⚠️ هذا الطلب ليس لك.")

    # تشغيل عملية التحميل كمهمة مستقلة تماماً
    asyncio.create_task(process_download(e, data, type_dl))

async def process_download(event, data, type_dl):
    """هذه الدالة تعمل بشكل مستقل لكل مستخدم"""
    uid = uuid.uuid4().hex
    # إنشاء مجلد فريد لهذه العملية فقط لمنع التداخل
    task_dir = f"downloads/{uid}"
    os.makedirs(task_dir, exist_ok=True)
    file_path = f"{task_dir}/media"

    await event.edit("⏳ جاري التحميل والمعالجة المستقلة...")

    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
        "n_threads": 4, # تخصيص موارد لكل عملية
    }

    if type_dl == 'v':
        # التحميل بأفضل جودة MP4 لضمان الإرسال كفيديو مشغل
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_ops["merge_output_format"] = "mp4"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    try:
        # التحميل (يتم في Thread منفصل عبر run_sync)
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = await run_sync(ydl.extract_info, data['u'], True)
            
        # تحديد الملف الناتج داخل المجلد الفريد
        downloaded_file = next((f"{task_dir}/{f}" for f in os.listdir(task_dir) if f.startswith("media")), None)
        
        if not downloaded_file:
            raise Exception("لم يتم العثور على الملف.")

        # إعداد السمات لضمان العرض كفيديو
        if type_dl == 'v':
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"✅ **تم التحميل:**\n`{info['title']}`",
                attributes=[DocumentAttributeVideo(
                    duration=int(info.get('duration', 0)),
                    w=info.get('width', 0),
                    h=info.get('height', 0),
                    supports_streaming=True
                )],
                force_document=False
            )
        else:
            await ABH.send_file(
                event.chat_id, downloaded_file,
                caption=f"🎵 **تم تحميل الصوت:**\n`{info['title']}`",
                attributes=[DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'))]
            )
        
        await event.delete()

    except Exception as ex:
        await event.edit(f"❌ خطأ أثناء التحميل: {str(ex)[:100]}")
    
    finally:
        # حذف المجلد الفريد بالكامل بعد الانتهاء (نجاح أو فشل)
        await run_sync(shutil.rmtree, task_dir, ignore_errors=True)

# --- تشغيل البوت ---
print("🚀 البوت يعمل الآن بنظام المهام المستقلة (Asyncio Tasks)...")
ABH.run_until_disconnected()
