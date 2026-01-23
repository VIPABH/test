import asyncio, yt_dlp, os, re, uuid
from telethon.tl.types import DocumentAttributeAudio
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from Resources import hint
from ABH import ABH, r

# --- 1. الدوال المساعدة (Helper Functions) ---

async def run_sync(func, *args):
    """لتشغيل العمليات المتزامنة بشكل غير متزامن"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def get_yt_results(query, limit=10):
    """دالة منفردة للبحث في يوتيوب"""
    return Y88F8(query, max_results=limit).to_dict()

def execute_download(ydl_ops, url):
    """دالة منفردة للتعامل مع مكتبة yt_dlp"""
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

# --- 2. دوال المنطق البرمجي (Logic Functions) ---

async def show_download_options(event, url, title="رابط مباشر"):
    """دالة منفردة لعرض أزرار اختيار الجودة (فيديو/صوت)"""
    short_id = str(uuid.uuid4())[:8]
    r.setex(f"yt_tmp:{short_id}", 600, url)
    
    buttons = [
        [
            Button.inline("🎥 تحميل فيديو", data=f"dl_v|{short_id}"),
            Button.inline("🎵 تحميل صوت (MP3)", data=f"dl_a|{short_id}")
        ]
    ]
    await event.reply(f"**🎬 العنوان:** `{title}`\n\nاختر نوع الملف الذي تريده:", buttons=buttons)

async def process_yt_search(event, query):
    """دالة منفردة لمعالجة نص البحث وعرض النتائج"""
    try:
        results = await run_sync(get_yt_results, query)
        if not results:
            return await event.reply("❌ ما لكيت نتائج بحث.")
        
        msg = f"🔍 **نتائج البحث عن:** `{query}`\n\n"
        for i, res in enumerate(results, 1):
            msg += f"{i} - **{res['title']}**\n"
            msg += f"🔗 للتحميل: `/dl_{res['id']}`\n\n"
        
        await event.reply(msg)
    except Exception as ex:
        await hint(f"Search Error: {str(ex)}")
        await event.reply("❌ حدث خطأ أثناء البحث.")

# --- 3. معالجات الأحداث (Event Handlers) ---

@ABH.on(events.NewMessage)
async def main_handler(e):
    """المعالج الرئيسي للرسائل الجديدة"""
    if not e.is_private or not e.text:
        return
    
    input_str = e.text.strip()
    
    # حالة كود التحميل المباشر
    if input_str.startswith('/dl_'):
        vid_id = input_str.replace('/dl_', '')
        return await show_download_options(e, f"https://youtu.be/{vid_id}", "فيديو يوتيوب")

    if re.match(r'^https?://', input_str):
        return await show_download_options(e, input_str)
    await process_yt_search(e, input_str)
@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def download_callback_handler(e):
    """المعالج الخاص بضغطات أزرار التحميل"""
    data = e.data.decode("utf-8").split("|")
    type_dl, short_id = data[0], data[1]
    url = r.get(f"yt_tmp:{short_id}")
    if not url:
        return await e.answer("⚠️ انتهت صلاحية الطلب.", alert=True)
    url = url.decode("utf-8") if isinstance(url, bytes) else url
    await e.edit("⏳ جاري التحميل... يرجى الانتظار")
    ydl_ops = {
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "quiet": True, "no_warnings": True, "logger": None,
        "outtmpl": f"downloads/{e.sender_id}_%(title)s.%(ext)s",
    }
    if type_dl == "dl_v":
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{
            "key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192",
        }]
    try:
        info = await run_sync(execute_download, ydl_ops, url)
        file_path = info.get('filepath') or info['requested_downloads'][0]['filepath']
        if type_dl == "dl_a" and not file_path.endswith(".mp3"):
            new_p = os.path.splitext(file_path)[0] + ".mp3"
            if os.path.exists(new_p): file_path = new_p
        caption = f"**✅ تم التحميل:**\n[{info.get('title')}]({url})"
        attr = [DocumentAttributeAudio(duration=int(info.get('duration', 0)), 
                                      title=info.get('title'), 
                                      performer=info.get('uploader'))] if type_dl == "dl_a" else []
        await ABH.send_file(e.chat_id, file_path, caption=caption, attributes=attr, 
                            supports_streaming=(type_dl == "dl_v"))
        await e.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as ex:
        await e.edit(f"❌ خطأ: `{str(ex)[:100]}`")
