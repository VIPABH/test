import os
from telethon import TelegramClient, events
from youtubesearchpython import VideosSearch
import pathlib
from telethon.tl import types
from telethon.utils import get_attributes
from youtube_dl import YoutubeDL
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
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
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
        await event.edit("᯽︙ - يتم جلب البيانات انتظر قليلا")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await event.edit("᯽︙ - عذرا هذا المحتوى قصير جدا لتنزيله ⚠️")
        return None
    except GeoRestrictedError:
        await event.edit(
            "᯽︙ - الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب ❕"
        )
        return None
    except MaxDownloadsReached:
        await event.edit("᯽︙ - تم الوصول إلى الحد الأقصى لعدد التنزيلات ❕")
        return None
    except PostProcessingError:
        await event.edit("᯽︙ كان هناك خطأ أثناء المعالجة")
        return None
    except UnavailableVideoError:
        await event.edit("`الوسائط غير متوفرة بالتنسيق المطلوب`")
        return None
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return None
    except ExtractorError:
        await event.edit("᯽︙ حدث خطأ أثناء استخراج المعلومات يرجى وضعها بشكل صحيح ⚠️")
        return None
    except Exception as e:
        await event.edit(f"᯽︙ حدث خطا : \n__{str(e)}__")
        return None
    return ytdl_data


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
async def _get_file_name(path: pathlib.Path, full: bool = True) -> str:
    return str(path.absolute()) if full else path.stem + path.suffix

async def ytsearch(query, limit):
    result = ""
    videolinks = VideosSearch(query.lower(), limit=limit)
    for v in videolinks.result()["result"]:
        textresult = f"[{v['title']}](https://www.youtube.com/watch?v={v['id']})\n"
        try:
            textresult += f"**الشرح : **`{v['descriptionSnippet'][-1]['text']}`\n"
        except Exception:
            textresult += "**الشرح : **`None`\n"
        textresult += (
            f"**المدة : **{v['duration']}  **المشاهدات : **{v['viewCount']['short']}\n"
        )
        result += f"☞ {textresult}\n"
    return result
from telethon import events
from youtubesearchpython import VideosSearch

@ABH.on(events.NewMessage(pattern=r"^\.yt(?:\s+(\d+))?\s*(.+)?$"))
async def yt_search(event):
    query = event.pattern_match.group(2)  # استخراج استعلام البحث
    lim = event.pattern_match.group(1)    # استخراج عدد النتائج
    
    if not query:  # التحقق إذا لم يكن هناك بحث
        return await event.reply("**᯽︙ قم بكتابة البحث أو الرد على رسالة تحتوي عليه**")

    lim = int(lim) if lim else 10  # تعيين حد البحث (افتراضي 10)
    lim = min(max(lim, 1), 10)  # التأكد أن العدد بين 1 و 10

    video_q = await event.reply("**᯽︙ يتم البحث في اليوتيوب...**")

    try:
        search = VideosSearch(query, limit=lim)
        results = search.result()
    except Exception as e:
        return await video_q.edit(f"❌ **خطأ:** {str(e)}")

    if not results["result"]:  # التحقق إذا لم يتم العثور على نتائج
        return await video_q.edit("❌ **لم يتم العثور على نتائج!**")

    # تنسيق النتائج
    reply_text = f"**🔎 نتائج البحث عن:** `{query}`\n\n"
    for video in results["result"]:
        title = video["title"]
        link = video["link"]
        reply_text += f"🎥 [{title}]({link})\n"

    await video_q.edit(reply_text)

# @ABH.on(events.NewMessage)
# async def yt_search(event):
#     query = event.text()
#     video_q = await event.reply(event, "**᯽︙ يتم البحث في اليوتيوب**")
#     if event.pattern_match.group(1) != "":
#         lim = int(event.pattern_match.group(1))
#         if lim <= 0:
#             lim = 10
#     else:
#         lim = 10
#     try:
#         full_response = await ytsearch(query, limit=lim)
#     except Exception as e:
#         return await event.reply(video_q, str(e), time=10)
#     reply_text = f"**•  البحث المطلوب:**\n`{query}`\n\n**•  النتائج:**\n{full_response}"
#     await event.reply(video_q, reply_text)
ABH.run_until_disconnected()
