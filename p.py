from telethon import TelegramClient, events, Button
import requests
import uuid
import os
import urllib.parse

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

downloadLinks = {}

async def youtubeAll(query):
    try:
        encoded_query = urllib.parse.quote_plus(query)
        response = requests.get(f"https://ochinpo-helper.hf.space/yt?query={encoded_query}", timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            raise Exception("لا يوجد فيديو متاح للتحميل.")
        info = data["result"]
        return {
            "title": info.get("title", "غير معروف"),
            "url": info.get("url"),
            "description": info.get("description", ""),
            "audio_download": info["download"]["audio"],
            "video_download": info["download"]["video"],
            "thumbnail": info.get("thumbnail"),
            "authorsn": info.get("author", {}).get("name", "مجهول"),
            "views": info.get("views", "غير متوفر"),
            "ago": info.get("ago", "غير متوفر"),
            "duration": info.get("duration", {}).get("timestamp", "غير معروف"),
            "timestamp": info.get("timestamp", "غير متوفر")
        }
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return None

async def downloadFile(url, filename):
    try:
        encoded_url = urllib.parse.quote_plus(url)
        final_url = f"https://ochinpo-helper.hf.space/yt/dl?url={encoded_url}&type={'audio' if filename.endswith('.mp3') else 'video'}"
        response = requests.get(final_url, stream=True, timeout=60)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return filename
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

@bot.on(events.NewMessage(pattern=r"^يوت (.+)"))
async def ytdl(event):
    query = event.pattern_match.group(1)
    result = await youtubeAll(query)
    if not result:
        await event.reply("『⚠️』عذرًا، لم يتم العثور على الفيديو المطلوب.")
        return
    audioId = str(uuid.uuid4())[:8]
    videoId = str(uuid.uuid4())[:8]
    downloadLinks[audioId] = result['audio_download']
    downloadLinks[videoId] = result['video_download']
    buttons = [
        [Button.inline("『🎶』تحميل الصوت", f"audio_{audioId}")],
        [Button.inline("『📹』تحميل الفيديو", f"video_{videoId}")]
    ]
    msg = f"『🎬』**{result['title']}**\n"
    msg += f"『👤』{result['authorsn']}\n"
    msg += f"『👀』{result['views']}\n"
    msg += f"『⏳』{result['duration']}\n"
    msg += f"『📅』{result['ago']}\n"
    await event.reply(msg, file=result["thumbnail"], buttons=buttons)

@bot.on(events.CallbackQuery)
async def callbacks(event):
    data = event.data.decode("utf-8")
    action, linkId = data.split("_", 1)
    if linkId in downloadLinks:
        url = downloadLinks[linkId]
        filename = f"{linkId}.mp4" if action == "video" else f"{linkId}.mp3"
        await event.edit("『📥』جاري التحميل...")
        filepath = await downloadFile(url, filename)
        if filepath:
            await event.respond(file=filepath)
            await event.delete()
            os.remove(filepath)
        else:
            await event.edit("『⚠️』فشل التحميل، حاول لاحقًا.")
        downloadLinks.pop(linkId, None)

print("『✅』البوت يعمل الآن...")
bot.run_until_disconnected()
