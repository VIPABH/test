import yt_dlp, os, re, time, wget, json
from youtube_search import YoutubeSearch as Y88F8
from ABH  import *
@ABH.on(events.NewMessage(pattern=r'^(يوت|yt|حمل|تحميل)\s*(.*)$'))
async def yt_func(e):
    query = e.pattern_match.group(2)
    if not query:
        r = await e.get_reply_message()
        if r and r.text:
            query = r.text
        else:
            return await e.reply("😑")
    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return await e.reply("لم يتم العثور على نتائج.")
    res = results[0]
        # if ytdb.get(f'ytvideo{res["id"]}'):
        #     aud = ytdb.get(f'ytvideo{res["id"]}')
        #     duration_string = time.strftime('%M:%S', time.gmtime(aud["duration"]))
        #     return e.reply_audio(
        #         aud["audio"],
        #         caption=f'@{channel} ~ {duration_string} ⏳',
        #         reply_markup=rep
        #     )
    url = f'https://youtu.be/{res["id"]}'
    ydl_ops = {
        "format": "bestaudio[ext=m4a]",
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "forceduration": True,
        "noplaylist": True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_ops) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            uploader = info.get('uploader')
            duration_string = time.strftime('%M:%S', time.gmtime(duration))
            audio_file = ydl.prepare_filename(info)
            ydl.download([url])
            os.rename(audio_file, audio_file.replace(".m4a", ".mp3"))
            audio_file = audio_file.replace(".m4a", ".mp3")
            thumb = wget.download(thumbnail)
            await ABH.send_file(
                e.chat_id,
                audio_file,
            )
            # ytdb.set(f'ytvideo{res["id"]}', {
            #     "type": "audio",
            #     "audio": a.audio.file_id,
            #     "duration": a.audio.duration
            # })
            os.remove(audio_file)
            os.remove(thumb)
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل الفيديو: {e}")
