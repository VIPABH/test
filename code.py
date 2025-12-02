import yt_dlp, os, time, wget, asyncio
from youtube_search import YoutubeSearch as Y88F8
from threading import Thread
from ABH import *
@ABH.on(events.NewMessage(pattern=r'^(حمل|يوت|تحميل|yt) (.+)'))
def ytdownloaderHandler(e):
    asyncio.create_task(yt_func(e))
async def yt_func(e):
    re = await e.get_reply_message()
    query = e.pattern_match.group(2)
    if not query:
        if re:
            query = re.text
        else:
            await e.reply('شنو تحب احملك وانت ما كاتب بحث')
    results = Y88F8(query, max_results=1).to_dict()
    if not results:
        return e.reply("لم يتم العثور على نتائج.")
    res = results[0]
    if r.get(f'ytvideo{res["id"]}'):
        aud = r.get(f'ytvideo{res["id"]}')
        duration_string = time.strftime('%M:%S', time.gmtime(aud["duration"]))
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
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            audio_file = ydl.prepare_filename(info)
            ydl.download([url])
            os.rename(audio_file, audio_file.replace(".m4a", ".mp3"))
            audio_file = audio_file.replace(".m4a", ".mp3")
            thumb = wget.download(thumbnail)
            a = await ABH.send_file(
                e.chat_id,
                audio_file,
                caption="[ENJOY DEAR](https://t.me/VIPABH_BOT)"
                )
            r.set(f'ytvideo{res["id"]}', {
                "type": "audio",
                "audio": a.audio.file_id,
                "duration": a.audio.duration
            })
            os.remove(audio_file)
            os.remove(thumb)
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل الفيديو: {e}")
        m.reply("حدث خطأ أثناء التحميل، يرجى المحاولة لاحقًا.")
