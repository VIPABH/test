import yt_dlp, os, time, wget, asyncio, json
from youtube_search import YoutubeSearch as Y88F8
from ABH import *
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from telethon import events


@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) (.+)'))
async def ytdownloaderHandler(e):
    asyncio.create_task(yt_func(e))


async def yt_func(e):
    try:
        re_msg = await e.get_reply_message()
        query = e.pattern_match.group(2)

        if not query:
            if re_msg:
                query = re_msg.text
            else:
                return await e.reply("شنو تحب احملك وانت ما كاتب بحث؟")

        results = Y88F8(query, max_results=1).to_dict()
        if not results:
            return await e.reply("ما لكيت أي نتيجة!")

        res = results[0]
        vid_id = res["id"]

        # =============== READ CACHE ===============
        cache = None
        try:
            raw = r.get(f"ytvideo{vid_id}")
            if raw:
                cache = json.loads(raw)
        except:
            cache = None

        # =============== SEND FROM CACHE ===============
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
                        caption=f"[ENJOY DEAR](https://t.me/VIPABH_BOT) {duration_string}"
                    )

                    return
                else:
                    pass  # تجاهل التحذير بدل الطباعة
            except:
                pass  # تجاهل أي خطأ أثناء إرسال الكاش

        # =============== DOWNLOAD NEW FILE ===============
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
            print(f"[YTDLP ERROR] {err}")
            return await e.reply("خطأ أثناء التحميل!")

        # تحميل الصورة
        try:
            thumb = wget.download(thumbnail)
        except:
            thumb = None

        # =============== SEND FILE ===============
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

        # =============== EXTRACT DATA ===============
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
            pass  # تجاهل أي خطأ في قراءة duration

        # =============== SAVE CACHE ===============
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
                pass  # تجاهل أي خطأ في حفظ الكاش

        # =============== CLEANUP ===============
        try:
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
            if thumb and os.path.exists(thumb):
                os.remove(thumb)
        except:
            pass

    except Exception as err:
        print(f"[GENERAL ERROR] {err}")
