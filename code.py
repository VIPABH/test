from telethon.tl.types import DocumentAttributeAudio, InputDocument
from youtube_search import YoutubeSearch as Y88F8
import yt_dlp, os, time, wget, asyncio, json
from telethon import events, Button
from Resources import hint, wfffp
from ABH import ABH, r
buttons = Button.url('🫆', url=f'https://t.me/{wfffp}')
b = Button.url('❤', url='https://t.me/ANYMOUSupdate')
async def chs(event, c):
    await ABH.send_message(event.chat_id, c, reply_to=event.id, buttons=buttons)
@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) ?(.*)', from_users=[wfffp]))
async def yt_func(e):
    re_msg = await e.get_reply_message()
    query = e.pattern_match.group(2)
    if not query:
        if re_msg:
            query = re_msg.text
        else:
            return await chs(e,"شنو تحب احملك وانت ما كاتب بحث؟")
    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return await chs(e,"ما لكيت أي نتيجة!")
    res = results[0]
    vid_id = res["id"]
    cache = None
    try:
        raw = r.get(f"ytvideo{vid_id}")
        if raw:
            cache = json.loads(raw)
    except:
        cache = None
    if cache:
        try:
            if (
                cache.get("audio_id") and
                cache.get("access_hash") and
                cache.get("file_reference")
            ):
                file = InputDocument(
                    id=cache["audio_id"],
                    access_hash=cache["access_hash"],
                    file_reference=bytes.fromhex(cache["file_reference"])
                )
                duration_string = time.strftime(
                    '%M:%S',
                    time.gmtime(cache.get("duration", 0))
                )
                await ABH.send_file(
                    e.chat_id,
                    file,
                    caption=f"[{duration_string}](https://t.me/VIPABH_BOT)",
                    buttons=b, 
                    reply_to=e.id
                )
                return
            else:
                pass
        except:
            pass  
    url = f"https://youtu.be/{vid_id}"
    ydl_ops = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "concurrent_fragment_downloads": 4
    }
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get("duration", 0)
            thumbnail = info.get("thumbnail")
            mp3_file = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
    except Exception as err:
        await hint(f"[YTDLP ERROR] {err}")
    try:
        thumb = wget.download(thumbnail)
    except:
        thumb = None
    sent = await ABH.send_file(
        e.chat_id,
        mp3_file,
        caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)",
        buttons=b,
        reply_to=e.id,
        attributes=[
            DocumentAttributeAudio(
                duration=duration,
                title=info.get("title", ""),
                performer=info.get("uploader", "")
            )
        ]
    )
    audio_id = None
    access_hash = None
    file_ref = None
    dur = duration
    try:
        if sent.audio:
            audio_id = sent.audio.id
            access_hash = sent.audio.access_hash
            file_ref = sent.audio.file_reference.hex()
            dur = sent.audio.duration
        else:
            audio_id = sent.document.id
            access_hash = sent.document.access_hash
            file_ref = sent.document.file_reference.hex()
            for attr in sent.document.attributes:
                if isinstance(attr, DocumentAttributeAudio):
                    dur = attr.duration
                    break
    except:
        pass  
    if audio_id and access_hash and file_ref:
        try:
            r.set(
                f"ytvideo{vid_id}",
                json.dumps({
                    "audio_id": audio_id,
                    "access_hash": access_hash,
                    "file_reference": file_ref,
                    "duration": dur
                })
            )
        except:
            pass
    try:
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
    except:
        pass
@ABH.on(events.NewMessage(pattern=r'^بوت', from_users=[wfffp]))
async def botinfo(e):
    await ABH.send_message(
        e.chat_id,
        "هلو عيني انا بوت تحميل من اليوتيوب اسمي [VIP ABH BOT](https://t.me/VIPABH_BOT) اتمنى تستمتع بخدماتي",
        buttons=Button.url("اضغط هنا للاشتراك", "https://t.me/VIPABH_BOT"),
        reply_to=e.id
    )
