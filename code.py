import asyncio, yt_dlp, os, re, uuid, json
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from Resources import hint
from ABH import ABH, r

# --- 1. الدوال المساعدة (Helper Functions) ---

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def get_yt_results(query, limit=10):
    return Y88F8(query, max_results=limit).to_dict()

def execute_download(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

# --- 2. دوال التخزين (Caching Logic) ---

def get_cached_media(media_key):
    """جلب بيانات الميديا من Redis إذا كانت موجودة"""
    cached = r.get(f"yt_cache:{media_key}")
    if cached:
        return json.loads(cached)
    return None

def save_media_to_cache(media_key, file_msg, type_dl):
    """حفظ بيانات الميديا (File ID) في Redis"""
    try:
        # استخراج بيانات الملف من الرسالة المرسلة
        media = file_msg.audio or file_msg.video or file_msg.document
        if not media: return
        
        data = {
            "file_id": media.id,
            "access_hash": media.access_hash,
            "file_reference": media.file_reference.hex(),
            "type": type_dl
        }
        # التخزين باستخدام المفتاح (الذي يكون إما ID الفيديو أو الرابط)
        r.set(f"yt_cache:{media_key}", json.dumps(data))
    except Exception as ex:
        print(f"Cache Save Error: {ex}")

# --- 3. دوال المنطق البرمجي (Logic Functions) ---

async def show_download_options(event, url, title="رابط مباشر"):
    # استخراج معرف فريد للرابط (Video ID) لاستخدامه في الكاش
    video_id = url.split("v=")[-1] if "v=" in url else url.split("/")[-1]
    
    short_id = str(uuid.uuid4())[:8]
    r.setex(f"yt_tmp:{short_id}", 600, json.dumps({"url": url, "vid": video_id}))
    
    buttons = [
        [
            Button.inline("🎥 فيديو", data=f"dl_v|{short_id}"),
            Button.inline("🎵 صوت (MP3)", data=f"dl_a|{short_id}")
        ]
    ]
    await event.reply(f"**🎬 العنوان:** `{title}`\n\nاختر نوع الملف:", buttons=buttons)

async def process_yt_search(event, query):
    try:
        results = await run_sync(get_yt_results, query)
        if not results: return await event.reply("❌ لم أجد نتائج.")
        
        msg = f"🔍 **نتائج البحث:** `{query}`\n\n"
        for i, res in enumerate(results, 1):
            msg += f"{i} - **{res['title']}**\n🔗 `/dl_{res['id']}`\n\n"
        await event.reply(msg)
    except Exception as ex:
        await event.reply(f"❌ خطأ بحث: {ex}")

# --- 4. معالجات الأحداث (Event Handlers) ---

@ABH.on(events.NewMessage)
async def main_handler(e):
    if not e.is_private or not e.text: return
    
    text = e.text.strip()
    if text.startswith('/dl_'):
        vid = text.replace('/dl_', '')
        return await show_download_options(e, f"https://youtu.be/{vid}", "فيديو يوتيوب")
    
    if re.match(r'^https?://', text):
        return await show_download_options(e, text)
    
    await process_yt_search(e, text)

@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    data = e.data.decode("utf-8").split("|")
    type_dl, short_id = data[0], data[1]
    
    # جلب بيانات الرابط والمعرف من التخزين المؤقت للزر
    tmp_data = r.get(f"yt_tmp:{short_id}")
    if not tmp_data: return await e.answer("⚠️ الطلب قديم.", alert=True)
    
    tmp_data = json.loads(tmp_data)
    url, video_id = tmp_data['url'], tmp_data['vid']
    
    # --- خطوة التحقق من التخزين (Cache Check) ---
    cache_key = f"{type_dl}:{video_id}"
    cached_file = get_cached_media(cache_key)
    
    if cached_file:
        await e.edit("🚀 تم العثور على الملف في التخزين، يتم الإرسال...")
        try:
            file_to_send = InputDocument(
                id=cached_file['file_id'],
                access_hash=cached_file['access_hash'],
                file_reference=bytes.fromhex(cached_file['file_reference'])
            )
            await ABH.send_file(e.chat_id, file_to_send, caption=f"**✅ تم الإرسال من التخزين**\n[{url}]({url})")
            return await e.delete()
        except Exception:
            pass # إذا فشل الـ File ID (مثلاً انتهت صلاحية المرجع)، ننتقل للتحميل العادي

    # --- خطوة التحميل (إذا لم يوجد في الكاش) ---
    await e.edit("⏳ الملف غير موجود، جاري التحميل والرفع...")
    
    ydl_ops = {
        "quiet": True, "no_warnings": True,
        "outtmpl": f"downloads/{e.sender_id}_%(title)s.%(ext)s",
    }
    if type_dl == "dl_v":
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        info = await run_sync(execute_download, ydl_ops, url)
        file_path = info.get('filepath') or info['requested_downloads'][0]['filepath']
        if type_dl == "dl_a" and not file_path.endswith(".mp3"):
            file_path = os.path.splitext(file_path)[0] + ".mp3"

        # إرسال الملف وحفظه في المتغير 'sent_msg'
        attr = [DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'))] if type_dl == "dl_a" else []
        sent_msg = await ABH.send_file(e.chat_id, file_path, caption=f"**✅ تم التحميل والحفظ**\n[{info.get('title')}]({url})", attributes=attr)
        
        # --- حفظ الملف في التخزين للمرة القادمة ---
        save_media_to_cache(cache_key, sent_msg, type_dl)
        
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as ex:
        await e.edit(f"❌ خطأ: `{str(ex)[:100]}`")
