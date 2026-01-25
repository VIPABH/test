import asyncio, yt_dlp, os, re, uuid, json
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from ABH import ABH, r 

# --- الدوال الأساسية ---
async def run_sync(func, *args):
    return await asyncio.get_event_loop().run_in_executor(None, func, *args)

def extract_data(text):
    yt = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|shorts/|)([0-9A-Za-z_-]{11}))', text)
    ig = re.search(r'(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+))', text)
    if yt: return "youtube", yt.group(1), yt.group(2)
    if ig: return "instagram", ig.group(1), ig.group(2)
    return None, None, None

# --- معالج الرسائل ---
@ABH.on(events.NewMessage(incoming=True))
async def handler(e):
    if not e.is_private or not e.text: return
    p, url, vid = extract_data(e.text.strip())
    
    if p:
        sid = str(uuid.uuid4())[:8]
        r.setex(f"tmp:{sid}", 600, json.dumps({"u": url, "v": vid, "p": p, "id": e.sender_id}))
        btns = [[Button.inline("🎥 فيديو أصلي", data=f"v|{sid}"), Button.inline("🎵 صوت MP3", data=f"a|{sid}")]]
        await e.reply(f"**✅ تم كشف رابط {p.upper()}**\nاختر النوع للتحميل المباشر:", buttons=btns)
    elif not e.text.startswith('/'):
        # بحث سريع
        res = Y88F8(e.text, max_results=5).to_dict()
        msg = "\n".join([f"• **{r['title']}**\n🔗 `https://youtu.be/{r['id']}`" for r in res])
        await e.reply(msg or "❌ لا توجد نتائج.")

# --- محرك التحميل والإرسال ---
@ABH.on(events.CallbackQuery(pattern=r'^(v|a)\|'))
async def dl_callback(e):
    data = json.loads(r.get(f"tmp:{e.data.decode().split('|')[1]}") or "{}")
    if not data or data['id'] != e.sender_id: return await e.answer("⚠️ انتهى الطلب.")
    
    type_dl = e.data.decode().split('|')[0]
    await e.edit("⏳ جاري سحب الملف الأصلي...")
    
    uid = uuid.uuid4().hex
    path = f"downloads/{uid}"
    
    # خيارات التحميل الخام (Original Quality)
    ydl_ops = {
        "quiet": True,
        "outtmpl": f"{path}.%(ext)s",
        "format": "bestvideo+bestaudio/best" if type_dl == 'v' else "bestaudio/best",
    }
    if type_dl == 'a':
        ydl_ops["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = await run_sync(ydl.extract_info, data['u'], True)
            
        # العثور على الملف المرسل
        file = next((f"downloads/{f}" for f in os.listdir("downloads") if f.startswith(uid)), None)
        
        # الإرسال كفيديو مباشر
        attrs = []
        if type_dl == 'v':
            attrs = [DocumentAttributeVideo(duration=int(info.get('duration', 0)), w=info.get('width', 0), h=info.get('height', 0), supports_streaming=True)]
        else:
            attrs = [DocumentAttributeAudio(duration=int(info.get('duration', 0)), title=info.get('title'))]

        await ABH.send_file(e.chat_id, file, caption=f"**✅ جودة أصلية:**\n`{info['title']}`", attributes=attrs, force_document=False)
        await e.delete()
    except Exception as ex:
        await e.edit(f"❌ فشل: {ex}")
    finally:
        for f in os.listdir("downloads"):
            if f.startswith(uid): os.remove(f"downloads/{f}")

print("✅ البوت شغال بأبسط صورة...")
