import yt_dlp, os, time, wget, asyncio
from youtube_search import YoutubeSearch as Y88F8
from ABH import *
@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) (.+)'))
async def ytdownloaderHandler(e):
    asyncio.create_task(yt_func(e))
async def yt_func(e):
    re_msg = await e.get_reply_message()
    query = e.pattern_match.group(2)
    if not query:
        if re_msg:
            query = re_msg.text
        else:
            return await e.reply("شنو تحب احملك وانت ما كاتب بحث")
    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return await e.reply("لم يتم العثور على نتائج.")
    res = results[0]
    cached = r.get(f'ytvideo{res["id"]}')
    if cached:
        duration = time.strftime("%M:%S", time.gmtime(cached["duration"]))
        return await ABH.send_file(
            e.chat_id,
            cached["audio_id"],
            caption=f"تم السحب من الكاش — المدة {duration}"
        )
    url = f'https://youtu.be/{res["id"]}'
    ydl_ops = {
        "format": "bestaudio[ext=m4a]",
        "noplaylist": True,
        "cachedir": True,
        "quiet": True,
        "no_warnings": True,
        "concurrent_fragment_downloads": 3,
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=True)
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail')
            audio_file = ydl.prepare_filename(info)
            mp3_file = audio_file.replace(".m4a", ".mp3")
            os.rename(audio_file, mp3_file)
            thumb = wget.download(thumbnail)
            send = await ABH.send_file(
                e.chat_id,
                mp3_file,
                caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)"
            )
            r.set(
                f'ytvideo{res["id"]}',
                {
                    "type": "audio",
                    "audio_id": send.audio.id,
                    "access_hash": send.audio.access_hash,
                    "file_reference": send.audio.file_reference.hex(),
                    "duration": send.audio.duration,
                }
            )
            os.remove(mp3_file)
            os.remove(thumb)
    except Exception as err:
        print(f"حدث خطأ أثناء التحميل: {err}")
