import yt_dlp, os, time, wget, asyncio
from youtube_search import YoutubeSearch as Y88F8
from ABH import *

@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) (.+)'))
async def ytdownloaderHandler(e):
    asyncio.create_task(yt_func(e))

async def yt_func(e):
    re = await e.get_reply_message()
    query = e.pattern_match.group(2)

    if not query:
        if re:
            query = re.text
        else:
            return await e.reply("شنو تحب احملك وانت ما كاتب بحث")

    # ============================
    #       البحث عن الفيديو
    # ============================
    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return await e.reply("لم يتم العثور على نتائج.")
    res = results[0]
    vid_id = res["id"]

    # ============================
    #   كاش البحث (Turbo Cache)
    # ============================
    cache = r.get(f'ytvideo{vid_id}')
    if cache:
        duration_string = time.strftime('%M:%S', time.gmtime(cache["duration"]))
        try:
            await ABH.send_file(
                e.chat_id,
                cache["audio_id"],   # إرسال مباشر بدون تحميل
                caption=f"[ENJOY DEAR](https://t.me/VIPABH_BOT) {duration_string}"
            )
        except:
            pass
        return

    url = f"https://youtu.be/{vid_id}"

    # ============================
    #   Turbo yt-dlp Settings
    # ============================
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
        "cachedir": True,
        "concurrent_fragment_downloads": 4,  # تحميل أسرع
        "username": os.environ.get("u"),
        "password": os.environ.get("p")
    }

    try:
        # التحميل
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get("duration", 0)
            thumbnail = info.get("thumbnail")
            mp3_file = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        # تحميل الصورة
        thumb = wget.download(thumbnail)

        # ============================
        #         إرسال الصوت
        # ============================
        sent = await ABH.send_file(
            e.chat_id,
            mp3_file,
            caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)",
            attributes=[
                DocumentAttributeAudio(
                    duration=duration,
                    title=info.get("title", ""),
                    performer=info.get("uploader", "")
                )
            ]
        )

        # ============================
        #   معالجة - Audio or Document
        # ============================
        if hasattr(sent, "audio") and sent.audio:
            audio_id = sent.audio.id
            access_hash = sent.audio.access_hash
            file_ref = sent.audio.file_reference.hex()
            dur = sent.audio.duration
        else:
            audio_id = sent.document.id
            access_hash = sent.document.access_hash
            file_ref = sent.document.file_reference.hex()
            dur = duration

        # ============================
        #         حفظ في الكاش
        # ============================
        r.set(
            f'ytvideo{vid_id}',
            {
                "audio_id": audio_id,
                "access_hash": access_hash,
                "file_reference": file_ref,
                "duration": dur
            }
        )

        os.remove(mp3_file)
        os.remove(thumb)

    except:
        pass   # بدون Logs
