from telethon import TelegramClient, events, Button
import requests
import uuid
import os

api_id = 
api_hash = ""
bot_token = ""

bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

downloadLinks = {}

async def youtubeAll(query):
    try:
        response = requests.get(f"https://ochinpo-helper.hf.space/yt?query={query}")
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        data = response.json()
        if not data.get("success"):
            raise Exception("No video found")
        info = data["result"]
        return {
            "title": info["title"],
            "url": info["url"],
            "description": info["description"],
            "audio_download": info["download"]["audio"],
            "video_download": info["download"]["video"],
            "thumbnail": info["thumbnail"],
            "authorsn": info["author"]["name"],
            "views": info["views"],
            "ago": info["ago"],
            "duration": info["duration"]["timestamp"],
            "timestamp": info["timestamp"]
        }
    except Exception as e:
        return None
        
async def downloadFile(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
        return None
    except Exception as e:
        return None

@bot.on(events.NewMessage(pattern=r"^يوت (.+)"))
async def ytdl(event):
    query = event.pattern_match.group(1)
    result = await youtubeAll(query)
    if not result:
        await event.reply("Do you know what I found?\nHaha nothing.")
        return
    audioId = str(uuid.uuid4())[:8]
    videoId = str(uuid.uuid4())[:8]
    downloadLinks[audioId] = result['audio_download']
    downloadLinks[videoId] = result['video_download']
    buttons = [
        [Button.inline("『🎶』Download audio", f"audio_{audioId}")],
        [Button.inline("『📹』Download video", f"video_{videoId}")]
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
        await event.edit("『📥』Loading...")
        filepath = await downloadFile(url, filename)
        if filepath:
            await event.respond(file=filepath)
            await event.delete()
            os.remove(filepath)
        else:
            await event.edit("『⚠️』Download Error")
        del downloadLinks[linkId]


print("『🔻』Running...")
bot.run_until_disconnected()
