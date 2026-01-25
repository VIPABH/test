import asyncio, yt_dlp, os, re, uuid, json, logging
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r

# إعداد السجلات لمتابعة الأخطاء
logging.basicConfig(level=logging.INFO)

# --- 1. تحسين الدوال المساعدة ---
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def get_video_id(url):
    """استخراج المعرف بشكل احترافي يدعم كل أنواع الروابط"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else str(uuid.uuid4())[:11]

# --- 2. إدارة التحميل الآمنة ---
def execute_download(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        # استخراج المعلومات أولاً لتجنب الأخطاء
        info = ydl.extract_info(url, download=True)
        return info

# --- 3. تعزيز منطق الكاش ---
def get_cached_media(media_key):
    cached = r.get(f"yt_cache:{media_key}")
    if cached:
        try:
            return json.loads(cached)
        except: return None
    return None

def save_media_to_cache(media_key, file_msg, type_dl):
    try:
        media = file_msg.audio or file_msg.video or file_msg.document
        if not media: return
        data = {
            "file_id": media.id,
            "access_hash": media.access_hash,
            "file_reference": media.file_reference.hex(),
            "type": type_dl
        }
        # تخزين لمدة 24 ساعة لأن المراجع تنتهي
        r.setex(f"yt_cache:{media_key}", 86400, json.dumps(data))
    except Exception as e:
        logging.error(f"Cache Error: {e}")

# --- 4. معالجات الأحداث المحسنة ---
@ABH.on(events.NewMessage(incoming=True))
async def main_handler(e):
    if not e.is_private or not e.text: return
    text = e.text.strip()

    # معالجة روابط يوتيوب أو البحث
    if re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/.+', text):
        await show_download_options(e, text)
    elif text.startswith('/dl_'):
        vid = text.split('_')[1]
        await show_download_options(e, f"https://youtu.be/{vid}")
    elif not text.startswith('/'):
        # البحث
        try:
            results = await run_sync(lambda: Y88F8(text, max_results=8).to_dict())
            if not results: return await e.reply("❌ لم يتم العثور على نتائج.")
            
            msg = f"🔍 **نتائج البحث لـ:** `{text}`\n\n"
            buttons = []
            for res in results:
                msg += f"• **{res['title']}**\n🔗 `/dl_{res['id']}`\n\n"
            await e.reply(msg, link_preview=False)
        except Exception as ex:
            await e.reply(f"❌ خطأ في البحث: {ex}")

async def show_download_options(event, url, title="يوتيوب"):
    video_id = get_video_id(url)
    short_id = str(uuid.uuid4())[:8]
    
    # حفظ البيانات مع ربطها بمعرف المستخدم لزيادة الأمان
    r.setex(f"yt_tmp:{short_id}", 600, json.dumps({"url": url, "vid": video_id, "u": event.sender_id}))
    
    buttons = [
        [Button.inline("🎥 فيديو (MP4)", data=f"dl_v|{short_id}"),
         Button.inline("🎵 صوت (MP3)", data=f"dl_a|{short_id}")]
    ]
    await event.reply(f"**🎬 معالجة الرابط...**\n`{url}`", buttons=buttons)

@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    raw_data = e.data.decode('utf-8')
    type_dl, short_id = raw_data.split("|")
    
    raw_tmp = r.get(f"yt_tmp:{short_id}")
    if not raw_tmp: return await e.answer("⚠️ الطلب انتهت صلاحيته.", alert=True)
    
    tmp_data = json.loads(raw_tmp)
    # التحقق أن المستخدم الذي ضغط هو صاحب الطلب
    if tmp_data['u'] != e.sender_id:
        return await e.answer("⚠️ هذا الزر ليس لك.", alert=True)

    url, video_id = tmp_data['url'], tmp_data['vid']
    cache_key = f"{type_dl}:{video_id}"
    
    # محاولة الإرسال من الكاش
    cached = get_cached_media(cache_key)
    if cached:
        try:
            file = InputDocument(
                id=cached['file_id'], 
                access_hash=cached['access_hash'], 
                file_reference=bytes.fromhex(cached['file_reference'])
            )
            await ABH.send_file(e.chat_id, file, caption=f"✅ **تم الإرسال من الكاش**\n🔗 {url}")
            return await e.delete()
        except: 
            r.delete(f"yt_cache:{cache_key}") # حذف الكاش إذا انتهت صلاحية المرجع

    await e.edit("⏳ **جاري التحميل والمعالجة...**")
    
    # إعدادات متطورة لـ yt-dlp
    file_path = f"downloads/{e.sender_id}_{uuid.uuid4().hex}"
    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }

    if type_dl == "dl_v":
        ydl_ops["format"] = "best[ext=mp4]/best"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    actual_file = None
    try:
        info = await run_sync(execute_download, ydl_ops, url)
        # تحديد المسار الصحيح للملف بعد التحميل
        if type_dl == "dl_a":
            actual_file = f"{file_path}.mp3"
        else:
            actual_file = info.get('filepath') or f"{file_path}.mp4"

        # الرفع للتليجرام
        sent = await ABH.send_file(
            e.chat_id, 
            actual_file, 
            caption=f"✅ **تم التحميل بنجاح**\n🎬 {info.get('title')}",
            supports_streaming=True
        )
        
        save_media_to_cache(cache_key, sent, type_dl)
        await e.delete()

    except Exception as ex:
        logging.error(f"Download Error: {ex}")
        await e.edit(f"❌ **عذراً، فشل التحميل.**\nالسبب: قيود من يوتيوب أو رابط غير مدعوم.")
    
    finally:
        # تنظيف الملفات دائماً (سواء نجح أو فشل)
        for ext in [".mp4", ".mp3", ".webm", ".m4a"]:
            full_p = f"{file_path}{ext}"
            if os.path.exists(full_p):
                os.remove(full_p)
