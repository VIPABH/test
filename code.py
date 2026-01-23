from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
import asyncio, yt_dlp, json, os, re
from Resources import wfffp

from ABH import ABH, r

async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def download_generic(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) ?(.*)', from_users=[wfffp]))
async def yt_func(e):
    cmd = e.pattern_match.group(1)
    input_str = e.pattern_match.group(2)
    re_msg = await e.get_reply_message()

    if not input_str and re_msg:
        input_str = re_msg.text
    
    if not input_str:
        return await e.reply("أرسل الرابط أو نص البحث بعد الأمر.")

    # فحص هل المدخل رابط أم نص بحث
    is_url = re.match(r'^https?://', input_str)
    
    if is_url:
        url = input_str
        vid_id = input_str # سنستخدم الرابط كمعرف للكاش
    else:
        # إذا كان نصاً، ابحث في يوتيوب أولاً
        results = Y88F8(input_str, max_results=1).to_dict()
        if not results: return await e.reply("لم أجد نتائج للبحث!")
        vid_id = results[0]["id"]
        url = f"https://youtu.be/{vid_id}"

    # الكاش (Redis)
    raw = r.get(f"vcache:{vid_id}")
    if raw:
        try:
            cache = json.loads(raw)
            file = InputDocument(id=cache["id"], access_hash=cache["hash"], file_reference=bytes.fromhex(cache["ref"]))
            return await ABH.send_file(e.chat_id, file, reply_to=e.id)
        except: pass

    # إعدادات عامة تدعم جميع المواقع
    ydl_ops = {
        "format": "bestaudio/best", # سيحمل أفضل جودة صوت متاحة
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "quiet": True,
        "no_warnings": True,
        "logger": None,
        "outtmpl": "downloads/%(title)s.%(ext)s", # تنظيم الملفات
    }

    status = await e.reply("جاري جلب البيانات من الرابط...")
    
    try:
        info = await run_sync(download_generic, ydl_ops, url)
        file_path = info['requested_downloads'][0]['filepath']
        title = info.get("title", "File")
        duration = info.get("duration", 0)
        
        sent = await ABH.send_file(
            e.chat_id,
            file_path,
            reply_to=e.id,
            caption=f"**تم التحميل بنجاح ✅**\n[{title}]({url})",
            attributes=[DocumentAttributeAudio(duration=int(duration), title=title)]
        )

        # تخزين في الكاش
        r.set(f"vcache:{vid_id}", json.dumps({
            "id": sent.audio.id if hasattr(sent, 'audio') and sent.audio else sent.document.id,
            "hash": sent.audio.access_hash if hasattr(sent, 'audio') and sent.audio else sent.document.access_hash,
            "ref": (sent.audio.file_reference if hasattr(sent, 'audio') and sent.audio else sent.document.file_reference).hex()
        }), ex=86400) # كاش لمدة يوم واحد

        if os.path.exists(file_path): os.remove(file_path)
        await status.delete()

    except Exception as ex:
        await status.edit(f"⚠️ فشل التحميل. تأكد من الرابط أو إعدادات الحساب.\n\n`{str(ex)[:100]}`")
