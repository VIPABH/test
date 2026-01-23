import asyncio, yt_dlp, os, re, uuid, json
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from Resources import hint
from ABH import ABH, r

# --- 1. الدوال المساعدة ---
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def get_yt_results(query, limit=10):
    return Y88F8(query, max_results=limit).to_dict()

def execute_download(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

# --- 2. دوال التخزين (Caching) ---
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
        r.set(f"yt_cache:{media_key}", json.dumps(data))
    except: pass

# --- 3. عرض خيارات التحميل ---
async def show_download_options(event, url, title="رابط مباشر"):
    video_id = url.split("v=")[-1] if "v=" in url else url.split("/")[-1]
    video_id = video_id.split("&")[0].split("?")[0]
    short_id = str(uuid.uuid4())[:8]
    r.setex(f"yt_tmp:{short_id}", 600, json.dumps({"url": url, "vid": video_id}))
    buttons = [[Button.inline("🎥 فيديو (MP4)", data=f"dl_v|{short_id}"),
                Button.inline("🎵 صوت (MP3)", data=f"dl_a|{short_id}")]]
    await event.reply(f"**🎬 العنوان:** `{title}`\n\nاختر نوع الملف:", buttons=buttons)

# --- 4. معالجات الأحداث ---
@ABH.on(events.NewMessage)
async def main_handler(e):
    if not e.is_private or not e.text: return
    text = e.text.strip()
    if text.startswith('/dl_'):
        vid = text.replace('/dl_', '')
        return await show_download_options(e, f"https://youtu.be/{vid}", "يوتيوب")
    if re.match(r'^https?://', text):
        return await show_download_options(e, text)
    try:
        results = await run_sync(get_yt_results, text)
        if not results: return await e.reply("❌ لم أجد نتائج.")
        msg = f"🔍 **نتائج البحث لـ:** `{text}`\n\n"
        for i, res in enumerate(results, 1):
            msg += f"{i} - **{res['title']}**\n🔗 `/dl_{res['id']}`\n\n"
        await e.reply(msg)
    except Exception as ex: await e.reply(f"❌ خطأ: {ex}")

@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    raw_data = e.data.decode('utf-8')
    type_dl, short_id = raw_data.split("|")
    raw_tmp = r.get(f"yt_tmp:{short_id}")
    if not raw_tmp: return await e.answer("⚠️ الطلب قديم.", alert=True)
    tmp_data = json.loads(raw_tmp)
    url, video_id = tmp_data['url'], tmp_data['vid']

    cache_key = f"{type_dl}:{video_id}"
    cached = get_cached_media(cache_key)
    if cached:
        await e.edit("🚀 إرسال سريع من التخزين...")
        try:
            file = InputDocument(id=cached['file_id'], access_hash=cached['access_hash'], file_reference=bytes.fromhex(cached['file_reference']))
            await ABH.send_file(e.chat_id, file, caption=f"**✅ من التخزين:**\n{url}")
            return await e.delete()
        except: pass

    await e.edit("⏳ جاري التحميل... يرجى الانتظار")
    
    # --- إعدادات تخطي الحظر 403 ---
    ydl_ops = {
        "quiet": True, 
        "no_warnings": True,
        "outtmpl": f"downloads/{e.sender_id}_%(title)s.%(ext)s",
        "n_threads": 4,
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
        },
        "geo_bypass": True,
    }
    
    if type_dl == "dl_v":
        ydl_ops["format"] = "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_ops["postprocessor_args"] = {"ffmpeg": ["-c:v", "libx264", "-preset", "superfast", "-pix_fmt", "yuv420p", "-movflags", "faststart"]}
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        info = await run_sync(execute_download, ydl_ops, url)
        file_path = info.get('filepath') or info['requested_downloads'][0]['filepath']
        if type_dl == "dl_a" and not file_path.endswith(".mp3"):
            new_p = os.path.splitext(file_path)[0] + ".mp3"
            if os.path.exists(new_p): file_path = new_p

        title = info.get('title', 'Unknown')
        sent = await ABH.send_file(e.chat_id, file_path, caption=f"**✅ تم التحميل:**\n[{title}]({url})", supports_streaming=(type_dl == "dl_v"))
        save_media_to_cache(cache_key, sent, type_dl)
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as ex:
        await e.edit(f"❌ فشل (403 أو حظر): حاول مرة أخرى أو استخدم رابطاً آخر.")
