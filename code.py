import yt_dlp, os, re, time, wget, json
from youtube_search import YoutubeSearch as Y88F8
from threading import Thread
from Resources import *
from ABH import *
CHANNEL_KEY = 'x04ou'
channel = r.get(CHANNEL_KEY)
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))
def Find(text):
    m = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(m, text)
    return [x[0] for x in url]
@ABH.on(events.NewMessage(pattern='^(حمل|يوت|تحميل|yt) ?(.*)'))
async def ytdownloaderHandler(e):
    if not e.is_group:return        
    cmd = e.pattern_match.group(1)
    l = lock(e, "يوتيوب")    
    target = e.chat_id
    if cmd != 'حمل':
        if l:
            target = e.chat_id
        else:
            target = r.get('channel_hint')
    asyncio.create_task(yt_func(e, target))
async def yt_func(e, target):
    text = e.text
    if text.startswith('حمل ') or text.startswith('yt '):
        query = text.split(None, 1)[1]
        print(f"استعلام البحث: {query}")
        results = Y88F8(query, max_results=1).to_dict()
        print(f"نتائج البحث: {json.dumps(results, indent=2, ensure_ascii=False)}")
        if not results:
            return e.reply("لم يتم العثور على نتائج.")
        res = results[0]
        print(f"أول نتيجة: {res}")
        if r.get(f'ytvideo{res["id"]}'):
            aud = r.get(f'ytvideo{res["id"]}')
            duration_string = time.strftime('%M:%S', time.gmtime(aud["duration"]))
            return ABH.send_file(
                target,
                aud["audio"],
                caption=f'@{channel} ~ {duration_string} ⏳',
            )
        url = f'https://youtu.be/{res["id"]}'
        print(f"الرابط المستهدف: {url}")
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
                print(f"معلومات الفيديو من yt_dlp:\n{json.dumps(info, indent=2, ensure_ascii=False)}")
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
                a = await ABH.send_message(
                    e.chat_id,
                    audio_file,
                    thumb=thumb,
                    duration=duration,
                    caption=f'@{channel} ~ {duration_string} ⏳',
                    performer=uploader,
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
