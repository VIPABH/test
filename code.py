import yt_dlp, os, time, wget, asyncio
from youtube_search import YoutubeSearch as Y88F8
from ABH import *
from telethon.tl.types import DocumentAttributeAudio

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
                return await e.reply("شنو تحب احملك وانت ما كاتب بحث")

        # ============================
        #       البحث عن الفيديو
        # ============================
        try:
            results = Y88F8(query, max_results=1).to_dict()
        except Exception as err:
            print(f"[SEARCH ERROR] {err}")
            return await e.reply("صار خطأ بعملية البحث")

        if not results:
            return await e.reply("ما لكيت نتائج للبحث.")

        res = results[0]
        vid_id = res["id"]

        # ============================
        #       كاش البحث
        # ============================
        try:
            cache = r.get(f'ytvideo{vid_id}')
        except Exception as err:
            print(f"[REDIS ERROR] {err}")
            cache = None

        if cache:
            try:
                duration_string = time.strftime('%M:%S', time.gmtime(cache["duration"]))

                await ABH.send_file(
                    e.chat_id,
                    cache["audio_id"],
                    caption=f"[ENJOY DEAR](https://t.me/VIPABH_BOT) {duration_string}"
                )
            except Exception as err:
                print(f"[CACHE SEND ERROR] {err}")
            return

        url = f"https://youtu.be/{vid_id}"

        # ============================
        #       إعدادات yt-dlp
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
            "concurrent_fragment_downloads": 4,
            "username": os.environ.get("u"),
            "password": os.environ.get("p")
        }

        try:
            with yt_dlp.YoutubeDL(ydl_ops) as ydl:
                info = ydl.extract_info(url, download=True)
                duration = info.get("duration", 0)
                thumbnail = info.get("thumbnail")
                mp3_file = ydl.prepare_filename(info)
                mp3_file = mp3_file.replace(".webm", ".mp3").replace(".m4a", ".mp3")

        except Exception as err:
            print(f"[YTDLP ERROR] {err}")
            return await e.reply("صار خطأ بتحميل الصوت من يوتيوب")

        # تحميل الصورة
        try:
            thumb = wget.download(thumbnail)
        except Exception as err:
            print(f"[THUMBNAIL ERROR] {err}")
            thumb = None

        # ============================
        #        إرسال الصوت
        # ============================
        try:
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
        except Exception as err:
            print(f"[SEND ERROR] {err}")
            return await e.reply("خطأ أثناء إرسال الملف")

        # ============================
        #   معالجة – Audio or Document
        # ============================
        try:
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
        except Exception as err:
            print(f"[PARSE FILE ERROR] {err}")
            audio_id, access_hash, file_ref, dur = None, None, None, duration

        # ============================
        #      حفظ في الكاش
        # ============================
        try:
            r.set(
                f'ytvideo{vid_id}',
                {
                    "audio_id": audio_id,
                    "access_hash": access_hash,
                    "file_reference": file_ref,
                    "duration": dur
                }
            )
        except Exception as err:
            print(f"[REDIS SAVE ERROR] {err}")

        # ============================
        #     تنظيف الملفات
        # ============================
        try:
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
            if thumb and os.path.exists(thumb):
                os.remove(thumb)
        except Exception as err:
            print(f"[CLEANUP ERROR] {err}")

    except Exception as err:
        print(f"[GENERAL ERROR] {err}")
