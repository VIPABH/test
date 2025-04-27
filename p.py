import os
import uuid
import requests
from telethon import TelegramClient, events, Button
from asyncio import to_thread

# إعداد المتغيرات من بيئة النظام
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

# تهيئة العميل (البوت)
bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

# تخزين روابط التحميل المؤقتة
download_links = {}

async def youtube_all(query: str) -> dict | None:
    """البحث عن مقطع فيديو وتحميل بياناته."""
    try:
        response = requests.get(f"https://ochinpo-helper.hf.space/yt?query={query}", timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return None
        
        info = data["result"]
        return {
            "title": info["title"],
            "url": info["url"],
            "description": info["description"],
            "audio_download": info["download"]["audio"],
            "video_download": info["download"]["video"],
            "thumbnail": info["thumbnail"],
            "author_name": info["author"]["name"],
            "views": info["views"],
            "ago": info["ago"],
            "duration": info["duration"]["timestamp"],
            "timestamp": info["timestamp"],
        }
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching YouTube data: {e}")
        return None

async def download_file(url: str, filename: str) -> str | None:
    """تحميل ملف من رابط URL."""
    try:
        def download():
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        
        return await to_thread(download)
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

@bot.on(events.NewMessage(pattern=r"^يوت (.+)"))
async def handle_youtube_search(event):
    """معالجة البحث عن فيديو والرد بالأزرار."""
    query = event.pattern_match.group(1)
    result = await youtube_all(query)
    
    if not result:
        await event.reply("『⚠️』لم يتم العثور على أي نتيجة.")
        return

    audio_id = str(uuid.uuid4())[:8]
    video_id = str(uuid.uuid4())[:8]
    download_links[audio_id] = result['audio_download']
    download_links[video_id] = result['video_download']

    buttons = [
        [Button.inline("『🎶』تحميل صوت", f"audio_{audio_id}")],
        [Button.inline("『📹』تحميل فيديو", f"video_{video_id}")],
    ]

    message = (
        f"『🎬』**{result['title']}**\n"
        f"『👤』{result['author_name']}\n"
        f"『👀』{result['views']} مشاهدة\n"
        f"『⏳』{result['duration']}\n"
        f"『📅』قبل {result['ago']}"
    )

    await event.reply(message, file=result["thumbnail"], buttons=buttons)

@bot.on(events.CallbackQuery)
async def handle_callback(event):
    """معالجة الضغط على أزرار التحميل."""
    data = event.data.decode("utf-8")
    action, link_id = data.split("_", 1)

    if link_id not in download_links:
        await event.edit("『⚠️』الرابط غير صالح أو انتهت صلاحيته.")
        return

    url = download_links.pop(link_id)
    filename = f"{link_id}.mp4" if action == "video" else f"{link_id}.mp3"

    await event.edit("『⏳』جاري التحميل، انتظر قليلاً...")

    filepath = await download_file(url, filename)
    if filepath:
        await event.respond(file=filepath)
        await event.delete()
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
    else:
        await event.edit("『⚠️』فشل في تحميل الملف.")

if __name__ == "__main__":
    print("『✅』البوت يعمل الآن...")
    bot.run_until_disconnected()
