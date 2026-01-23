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

# 1. استقبال الأمر وإظهار الأزرار
@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) ?(.*)', from_users=[wfffp]))
async def yt_func(e):
    input_str = e.pattern_match.group(2)
    re_msg = await e.get_reply_message()

    if not input_str and re_msg:
        input_str = re_msg.text
    
    if not input_str:
        return await e.reply("أرسل الرابط أو نص البحث بعد الأمر.")

    # فحص هل هو رابط أم بحث
    is_url = re.match(r'^https?://', input_str)
    if not is_url:
        results = await run_sync(lambda: Y88F8(input_str, max_results=1).to_dict())
        if not results: return await e.reply("لم أجد نتائج للبحث!")
        url = f"https://youtu.be/{results[0]['id']}"
        title = results[0]['title']
    else:
        url = input_str
        title = "الرابط المختار"

    # إرسال الأزرار
    buttons = [
        [Button.inline("🎥 فيديو (MP4)", data=f"dl_v|{url}"),
         Button.inline("🎵 صوت (MP3)", data=f"dl_a|{url}")]
    ]
    await e.reply(f"**اختر نوع التحميل لـ:**\n`{title}`", buttons=buttons)

# 2. معالجة ضغطات الأزرار
@ABH.on(events.CallbackQuery(pattern=r'^dl_(v|a)\|'))
async def callback_dl(e):
    data = e.data.decode("utf-8").split("|")
    type_dl = data[0] # dl_v أو dl_a
    url = data[1]
    
    await e.edit("⏳ جاري البدء في التحميل... يرجى الانتظار")

    ydl_ops = {
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "quiet": True,
        "no_warnings": True,
        "logger": None,
        "outtmpl": f"downloads/{e.sender_id}_%(title)s.%(ext)s",
    }

    if type_dl == "dl_v":
        ydl_ops["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    else:
        ydl_ops["format"] = "bestaudio/best"
        ydl_ops["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        info = await run_sync(download_generic, ydl_ops, url)
        file_path = info.get('filepath') or info['requested_downloads'][0]['filepath']
        
        # تصحيح مسار MP3 إذا لزم الأمر
        if type_dl == "dl_a" and not file_path.endswith(".mp3"):
            file_path = os.path.splitext(file_path)[0] + ".mp3"

        title = info.get("title", "File")
        duration = info.get("duration", 0)

        attr = []
        if type_dl == "dl_a":
            attr = [DocumentAttributeAudio(duration=int(duration), title=title, performer="Downloader")]

        await ABH.send_file(
            e.chat_id, 
            file_path, 
            caption=f"**✅ تم التحميل:**\n[{title}]({url})",
            attributes=attr,
            supports_streaming=True if type_dl == "dl_v" else False
        )
        
        await e.delete() # حذف رسالة الأزرار بعد النجاح
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as ex:
        await e.edit(f"⚠️ خطأ: `{str(ex)[:100]}`")
