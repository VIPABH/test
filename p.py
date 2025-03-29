from telethon.tl.types import MessageEntityPre
from telethon.utils import add_surrogate
import hashlib
import re
import time
from typing import Dict, Tuple
from telethon.errors.rpcerrorlist import MessageNotModifiedError
import asyncio
import io
import os
import pathlib
import re
import time
from telethon.tl import types
from telethon.utils import get_attributes
from youtube_dl import YoutubeDL
from telethon import events, TelegramClient
from youtube_dl.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)
from youtubesearchpython import VideosSearch # type: ignore

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
async def ytsearch(query, limit):
    result = ""
    try:
        # التحقق مما إذا كانت النتيجة فارغة أو غير موجودة
        videolinks = VideosSearch(query.lower(), limit=limit)
        search_results = videolinks.result().get("result", [])

        if not search_results:
            return "لا توجد نتائج للبحث."

        for v in search_results:
            textresult = f"[{v['title']}](https://www.youtube.com/watch?v={v['id']})\n"
            
            # التعامل مع الأخطاء في حال كان هناك خطأ في استخراج الوصف
            try:
                description = v.get("descriptionSnippet", [])
                if description:
                    textresult += f"**الشرح : **`{description[-1].get('text', 'لا يوجد وصف')}`\n"
                else:
                    textresult += "**الشرح : **`لا يوجد وصف`\n"
            except Exception:
                textresult += "**الشرح : **`خطأ في جلب الوصف`\n"
            
            # التحقق من وجود مدة المشاهدة والمشاهدات
            textresult += f"**المدة : **{v.get('duration', 'غير متوفر')}  **المشاهدات : **{v.get('viewCount', {}).get('short', 'غير متوفرة')}\n"
            
            result += f"☞ {textresult}\n"
            
    except Exception as e:
        return f"حدث خطأ أثناء البحث: {str(e)}"
    
    return result


audio_opts = {
    "format": "bestaudio",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
    "outtmpl": "%(title)s.mp3",
    "quiet": True,
    "logtostderr": False,
}

video_opts = {
    "format": "best",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
    "outtmpl": "%(title)s.mp4",
    "logtostderr": False,
    "quiet": True,
}


async def ytdl_down(event, opts, url):
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        return
    except ContentTooShortError:
        return None
    except GeoRestrictedError:
        return None
    except MaxDownloadsReached:
        return None
    except PostProcessingError:
        return None
    except UnavailableVideoError:
        return None
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return None
    except ExtractorError:
        return None
    except Exception as e:
        return None
    return ytdl_data
_TASKS: Dict[str, Tuple[int, int]] = {}
async def md5(fname: str) -> str:
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def humanbytes(size: int) -> str:
    if size is None or isinstance(size, str):
        return ""

    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return f"{str(round(size, 2))} {dict_power_n[raised_to_pow]}B"

def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    seconds = round(seconds, 2)
    tmp = (
        (f"{str(days)} day(s), " if days else "")
        + (f"{str(hours)} hour(s), " if hours else "")
        + (f"{str(minutes)} minute(s), " if minutes else "")
        + (f"{str(seconds)} second(s), " if seconds else "")
    )

    return tmp[:-2]

class CancelProcess(Exception):
    """
    Cancel Process
    """
async def progress(
    current,
    total,
    gdrive,
    start,
    prog_type,
    file_name=None,
    is_cancelled=False,
    delay=5,
):  # sourcery no-metrics
    if is_cancelled is True:
        raise CancelProcess
    task_id = f"{gdrive.chat_id}.{gdrive.id}"
    if current == total:
        if task_id not in _TASKS:
            return
        del _TASKS[task_id]
        try:
            await gdrive.edit("`finalizing process ...`")
        except MessageNotModifiedError:
            pass
        except Exception as e:
            return
    now = time.time()
    if task_id not in _TASKS:
        _TASKS[task_id] = (now, now)
    start, last = _TASKS[task_id]
    elapsed_time = now - start
    oldtmp = ""
    if (now - last) >= delay:
        _TASKS[task_id] = (start, now)
        percentage = current * 100 / total
        speed = current / elapsed_time
        eta = round((total - current) / speed)
        elapsed_time = round(elapsed_time)
        if "upload" in prog_type.lower():
            status = "Uploading"
        elif "download" in prog_type.lower():
            status = "Downloading"
        else:
            return
        tmp = (
            f"`{humanbytes(current)} of {humanbytes(total)}"
            f" @ {humanbytes(speed)}`\n"
            f"**ETA :**` {time_formatter(eta)}`\n"
            f"**Duration :** `{time_formatter(elapsed_time)}`"
        )
        if tmp != oldtmp:
            if file_name:
                await gdrive.edit(
                    f"**{prog_type}**\n\n"
                    f"**File Name : **`{file_name}`**\nStatus**\n{tmp}"
                )
            else:
                await gdrive.edit(f"**{prog_type}**\n\n" f"**Status**\n{tmp}")
            oldtmp = tmp

async def fix_attributes(
    path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = False

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(duration, None, title, uploader)
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration, width, height, round_message, supports_streaming
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    for attr in attributes:
        if (
            isinstance(attr, types.DocumentAttributeAudio)
            and not audio
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not video
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not isinstance(attr, types.DocumentAttributeVideo)
        ):
            new_attributes.append(attr)
    return new_attributes, mime_type

@ABH.on(events.NewMessage(pattern=r"فيديو(?: |$)(\d*)? ?([\s\S]*)"))
async def download_audio(event):
    """To download audio from YouTube and many other sites."""
    url = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not url and rmsg:
        myString = rmsg.text
        url = re.search(r"(?P<url>https?://[^\s]+)", myString).group("url")
    if not url:
        return await event.reply(event, "᯽︙ - يجب وضع رابط لتحميله ❕")
    catevent = await event.reply(event, "᯽︙ يتم الاعداد انتظر")
    ytdl_data = await ytdl_down(catevent, audio_opts, url)
    if ytdl_data is None:

        return
    await catevent.edit(
        f"᯽︙ يتم لتحميل الأغنية:\
        \n᯽︙ {ytdl_data['title']}\
        \nبواسطة ᯽︙ {ytdl_data['uploader']}"
    )
    f = pathlib.Path(f"{ytdl_data['title']}.mp3".replace("|", "_"))
    catthumb = pathlib.Path(f"{ytdl_data['title']}.mp3.jpg".replace("|", "_"))
    if not os.path.exists(catthumb):
        catthumb = pathlib.Path(f"{ytdl_data['title']}.mp3.webp".replace("|", "_"))
    if not os.path.exists(catthumb):
        catthumb = None
    c_time = time.time()
    ul = io.open(f, "rb")
    uploaded = await event.client.fast_upload_file(
        file=ul,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, catevent, c_time, "upload", file_name=f)
        ),
    )
    ul.close()
    attributes, mime_type = await fix_attributes(f, ytdl_data, supports_streaming=True)
    media = types.InputMediaUploadedDocument(
        file=uploaded,
        mime_type=mime_type,
        attributes=attributes,
        thumb=await event.client.upload_file(catthumb) if catthumb else None,
    )
    await event.client.send_file(
        event.chat_id,
        file=media,
        reply_to=event.reply,
        caption=ytdl_data["title"],
        supports_streaming=True,
        force_document=False,
    )
    os.remove(f)
    if catthumb:
        os.remove(catthumb)
    await catevent.delete()

@ABH.on(events.NewMessage(pattern=r"فديو(?: |$)(\d*)? ?([\s\S]*)"))
async def download_video(event):
    """To download video from YouTube and many other sites."""
    url = event.pattern_match.group(1)
    rmsg = await event.get_reply_message()
    if not url and rmsg:
        myString = rmsg.text
        url = re.search(r"(?P<url>https?://[^\s]+)", myString).group("url")
    if not url:
        return await event.reply(event, "᯽︙ عـليك وضع رابـط اولا ليتـم تنـزيله")
    catevent = await event.reply(event, "᯽︙ يتم التحميل انتظر قليلا")

    ytdl_data = await ytdl_down(catevent, video_opts, url)
    if ytdl_down is None:
        return
    f = pathlib.Path(f"{ytdl_data['title']}.mp4".replace("|", "_"))
    catthumb = pathlib.Path(f"{ytdl_data['title']}.jpg".replace("|", "_"))
    if not os.path.exists(catthumb):
        catthumb = pathlib.Path(f"{ytdl_data['title']}.webp".replace("|", "_"))
    if not os.path.exists(catthumb):
        catthumb = None
    await catevent.edit(
        f"᯽︙ التحضيـر للـرفع انتظر:\
        \n᯽︙ {ytdl_data['title']}\
        \nبـواسطة *{ytdl_data['uploader']}*"
    )
    ul = io.open(f, "rb")
    c_time = time.time()
    attributes, mime_type = await fix_attributes(f, ytdl_data, supports_streaming=True)
    uploaded = await event.client.fast_upload_file(
        file=ul,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, catevent, c_time, "upload", file_name=f)
        ),
    )
    ul.close()
    media = types.InputMediaUploadedDocument(
        file=uploaded,
        mime_type=mime_type,
        attributes=attributes,
        thumb=await event.client.upload_file(catthumb) if catthumb else None,
    )
    await event.client.send_file(
        event.chat_id,
        file=media,
        reply_to=event.reply,
        caption=ytdl_data["title"],
    )
    os.remove(f)
    if catthumb:
        os.remove(catthumb)
    await event.delete()
    
def parse_pre(text):
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(add_surrogate(text)), language="")],
    )
@ABH.on(events.NewMessage(pattern=r"يوت(?: |$)(\d*)? ?([\s\S]*)"))
async def yt_search(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
    if not query:
        return await event.reply(
            event, "**᯽︙ قم بالرد على النص او كتابته مع الامر**"
        )
    video_q = await event.reply("**᯽︙ يتم البحث في اليوتيوب**")
    if event.pattern_match.group(1) != "":
        lim = int(event.pattern_match.group(1))
        if lim <= 0:
            lim = 10
    else:
        lim = 10
        full_response = await ytsearch(query, limit=lim)
        reply_text = f"**•  البحث المطلوب:**\n`{query}`\n\n**•  النتائج:**\n{full_response}"
    await event.reply(reply_text)
ABH.run_until_disconnected()
