import asyncio, yt_dlp, os, re, uuid, json, logging
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r  # تأكد من إعداد ABH (TelegramClient) و r (Redis) في ملف ABH

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# إنشاء مجلد التحميلات إذا لم يوجد
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- 1. الدوال المساعدة والمنطق ---

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def extract_media_data(text):
    """التعرف على المنصة واستخراج الرابط والمعرف"""
    yt_regex = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/|shorts/|)([0-9A-Za-z_-]{11}))'
    ig_regex = r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv|stories)/([A-Za-z0-9_-]+))'

    yt_match = re.search(yt_regex, text)
    if yt_match:
        return "youtube", yt_match.group(1), yt_match.group(2)

    ig_match = re.search(ig_regex, text)
    if ig_match:
        return "instagram", ig_match.group(1), ig_match.group(2)

    return None, None, None

def execute_download(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

# --- 2. نظام التخزين المؤقت (Cache) ---

def get_cached_media(media_key):
    cached = r.get(f"yt_cache:{media_key}")
    if cached:
        try: return json.loads(cached)
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
        r.setex(f"yt_cache:{media_key}", 86400, json.dumps(data)) # كاش لمدة يوم
    except Exception as e:
        logging.error(f"Cache Error: {e}")

# --- 3. معالج الرسائل الرئيسي ---

@ABH.on(events.NewMessage(incoming=True))
async def main_handler(e):
    if not e.is_private or not e.text: return
    text = e.text.strip()

    platform, clean_url, media_id = extract_media_data(text)

    if platform:
        return await show_download_options(e, clean_url, platform, media_id)
    
    elif text.startswith('/dl_'):
        vid = text.split('_')[1]
        return await show_download_options(e, f"https://youtu.be/{vid}", "youtube", vid)
    
    elif not text.startswith('/') and len(text) > 2:
        try:
            results = await run_sync(lambda: Y88F8(text, max_results=5).to_dict())
            if not results: return await e.reply("❌ لم يتم العثور على نتائج.")
            msg = f"🔍 **نتائج البحث:**\n\n"
            for res in results:
                msg += f"• **{res['title']}**\n🔗 `/dl_{res['id']}`\n\n"
            await e.reply(msg, link_preview=False)
        except Exception as ex:
            await e.reply(f"❌ خطأ في البحث: {ex}")

async def show_download_options(event, url, platform, media_id):
    short_id = str(uuid.uuid4())[:8]
    r.setex(f"yt_tmp:{short_id}", 600, json.dumps({
        "url": url, "vid": media_id, "u": event.sender_id, "p": platform
    }))
    
    buttons = [[
        Button.inline("🎥 فيديو", data=f"dl_v|{short_id}"),
        Button.inline("🎵 صوت", data=f"dl_a|{short_id}")
    ]]
    
    icon = "📺" if platform == "youtube" else "📸"
    await event.reply(f"**{icon} تم كشف رابط {platform.upper()}**\n\nاختر الصيغة:", buttons=buttons)

# --- 4. معالج التحميل الفعلي ---

@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    raw_data = e.data.decode('utf-8')
    type_dl, short_id = raw_data.split("|")
    
    raw_tmp = r.get(f"yt_tmp:{short_id}")
    if not raw_tmp: return await e.answer("⚠️ الطلب انتهت صلاحيته.", alert=True)
    
    tmp_data = json.loads(raw_tmp)
    if tmp_data['u'] != e.sender_id:
        return await e.answer("⚠️ هذا الطلب ليس لك.", alert=True)

    url, platform, video_id = tmp_data['url'], tmp_data['p'], tmp_data['vid']
    cache_key = f"{type_dl}:{video_id}"
    
    # محاولة الإرسال من الكاش
    cached = get_cached_media(cache_key)
    if cached:
        try:
            file = InputDocument(id=cached['file_id'], access_hash=cached['access_hash'], file_reference=bytes.fromhex(cached['file_reference']))
            await ABH.send_file(e.chat_id, file, caption=f"✅ **تم الإرسال من الكاش**\n🔗 {url}")
            return await e.delete()
        except: r.delete(f"yt_cache:{cache_key}")

    await e.edit(f"⏳ جاري معالجة {platform}... يرجى الانتظار")
    
    unique_name = f"{e.sender_id}_{uuid.uuid4().hex}"
    file_path = f"downloads/{unique_name}"
    
    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{file_path}.%(ext)s",
        "geo_bypass": True,
        "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    }

    if type_dl == "dl_v":
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        info = await run_sync(execute_download, ydl_ops, url)
        
        # تحديد الملف الناتج بدقة
        actual_file = None
        for ext in [".mp4", ".mp3", ".m4a", ".webm", ".mkv"]:
            if os.path.exists(f"{file_path}{ext}"):
                actual_file = f"{file_path}{ext}"
                break
        
        if not actual_file:
            raise Exception("لم يتم العثور على الملف المحمل.")

        sent = await ABH.send_file(
            e.chat_id, actual_file, 
            caption=f"✅ **تم التحميل بنجاح**\n🎬 {info.get('title', 'بدون عنوان')}",
            supports_streaming=(type_dl == "dl_v")
        )
        
        save_media_to_cache(cache_key, sent, type_dl)
        await e.delete()

    except Exception as ex:
        logging.error(f"Download Error: {ex}")
        await e.edit(f"❌ **فشل التحميل!**\nالسبب: قد يكون المقطع خاصاً أو محمياً.")
    
    finally:
        # تنظيف نهائي للمجلد
        for f in os.listdir("downloads"):
            if f.startswith(unique_name):
                try: os.remove(os.path.join("downloads", f))
                except: pass

print("البوت يعمل الآن...")
