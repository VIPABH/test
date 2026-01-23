import asyncio
import json
import os
import time
import yt_dlp
from youtube_search import YoutubeSearch as Y88F8
from telethon import events, Button
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from ABH import ABH, r
from Resources import hint, wfffp

# دالة مساعدة لتشغيل الوظائف المتزامنة في خيط منفصل
async def run_sync(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

def search_yt(query):
    return Y88F8(query, max_results=1).to_dict()

def download_yt(ydl_ops, url):
    with yt_dlp.YoutubeDL(ydl_ops) as ydl:
        return ydl.extract_info(url, download=True)

@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) ?(.*)', from_users=[wfffp]))
async def yt_func(e):
    query = e.pattern_match.group(2)
    re_msg = await e.get_reply_message()
    
    if not query:
        if re_msg: query = re_msg.text
        else: return await e.reply("شنو تحب احملك وانت ما كاتب بحث؟")

    # 1. البحث (بدون تجميد)
    results = await run_sync(search_yt, query)
    if not results: return await e.reply("ما لكيت أي نتيجة!")
    
    res = results[0]
    vid_id = res["id"]
    url = f"https://youtu.be/{vid_id}"

    # 2. فحص الكاش (سريع جداً)
    raw = r.get(f"ytvideo{vid_id}")
    if raw:
        cache = json.loads(raw)
        try:
            file = InputDocument(
                id=cache["audio_id"],
                access_hash=cache["access_hash"],
                file_reference=bytes.fromhex(cache["file_reference"])
            )
            return await ABH.send_file(e.chat_id, file, caption="تم الرفع من الكاش ⚡", reply_to=e.id)
        except: pass

    # 3. إعدادات التحميل (سرعة قصوى)
    ydl_ops = {
        "format": "bestaudio[ext=m4a]",
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "forceduration": True,
        "noplaylist": True
    }
    status_msg = await e.reply("جاري التحميل... يرجى الانتظار ⏳")
    try:
        info = await run_sync(download_yt, ydl_ops, url)
        mp3_file = info['requested_downloads'][0]['filepath']
        duration = info.get("duration", 0)
        title = info.get("title", "Unknown")
        performer = info.get("uploader", "YouTube")
    except Exception as err:
        return await status_msg.edit(f"حدث خطأ أثناء التحميل: {err}")
    sent = await ABH.send_file(
        e.chat_id,
        mp3_file,
        caption=f"**{title}**",
        reply_to=e.id,
        attributes=[DocumentAttributeAudio(duration=duration, title=title, performer=performer)]
    )
    try:
        r.set(f"ytvideo{vid_id}", json.dumps({
            "audio_id": sent.audio.id if sent.audio else sent.document.id,
            "access_hash": sent.audio.access_hash if sent.audio else sent.document.access_hash,
            "file_reference": (sent.audio.file_reference if sent.audio else sent.document.file_reference).hex(),
            "duration": duration
        }))
        if os.path.exists(mp3_file): os.remove(mp3_file)
        await status_msg.delete()
    except: pass
@ABH.on(events.NewMessage(pattern=r'^بوت', from_users=[wfffp]))
async def botinfo(e):
    await ABH.send_message(
        e.chat_id,
        "هلو عيني انا بوت تحميل من اليوتيوب اسمي [VIP ABH BOT](https://t.me/VIPABH_BOT) اتمنى تستمتع بخدماتي",
        buttons=Button.url("اضغط هنا للاشتراك", "https://t.me/VIPABH_BOT"),
        reply_to=e.id
    )
