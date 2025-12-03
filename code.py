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
            return await e.reply('شنو تحب احملك وانت ما كاتب بحث')

    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return await e.reply("لم يتم العثور على نتائج.")

    res = results[0]

    # ============================
    #   نظام الكاش (بدون أخطاء)
    # ============================
    cache = r.get(f'ytvideo{res["id"]}')
    if cache:
        duration_string = time.strftime('%M:%S', time.gmtime(cache["duration"]))
        try:
            await ABH.send_file(
                e.chat_id,
                cache["audio_id"],
                caption=f"[ENJOY DEAR](https://t.me/VIPABH_BOT) {duration_string}"
            )
        except:
            pass
        return

    url = f'https://youtu.be/{res["id"]}'

    # ============================
    #     إعدادات yt-dlp أسرع
    # ============================
    ydl_ops = {
        "format": "bestaudio[ext=m4a]",
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "forceduration": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "concurrent_fragment_downloads": 3
    }

    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get("duration", 0)
            audio_file = ydl.prepare_filename(info)
            thumbnail = info.get("thumbnail")

            mp3_file = audio_file.replace(".m4a", ".mp3")
            os.rename(audio_file, mp3_file)

            thumb = wget.download(thumbnail)

            # الإرسال
            sent = await ABH.send_file(
                e.chat_id,
                mp3_file,
                caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)"
            )

            # ============================
            #      تخزين الكاش بدون خطأ
            # ============================
            if hasattr(sent, "audio") and sent.audio:
                audio_data = sent.audio
                dur = audio_data.duration
                audio_id = audio_data.id
                access = audio_data.access_hash
                ref = audio_data.file_reference.hex()
            else:
                dur = duration
                audio_id = sent.document.id
                access = sent.document.access_hash
                ref = sent.document.file_reference.hex()

            r.set(
                f'ytvideo{res["id"]}',
                {
                    "type": "audio",
                    "audio_id": audio_id,
                    "access_hash": access,
                    "file_reference": ref,
                    "duration": dur
                }
            )

            os.remove(mp3_file)
            os.remove(thumb)

    except:
        pass   # بدون أي طباعة او Log
