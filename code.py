import yt_dlp, os, re, time, json, requests
from youtube_search import YoutubeSearch as Y88F8
from ABH import *
from Resources import *
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
    url = f'https://youtu.be/{res["id"]}'
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "username": os.environ.get("u"),
        "password": os.environ.get("p"),
        "forceduration": True,
        "noplaylist": True,
        "quiet": True,                 
        "no_warnings": True,           
        "ignoreerrors": True,          
        "progress_hooks": [],          
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            duration_string = time.strftime('%M:%S', time.gmtime(duration))
            audio_file = ydl.prepare_filename(info)
            ydl.download([url])
            new_audio = audio_file.replace(".m4a", ".mp3")
            os.rename(audio_file, new_audio)
            thumb_name = "thumb.jpg"
            with open(thumb_name, "wb") as f:
                f.write(requests.get(thumbnail).content)
            await ABH.send_file(
                wfffp,
                new_audio,
            )
            os.remove(new_audio)
            os.remove(thumb_name)
    except Exception as err:
        await hint(f"Error: {err}")
