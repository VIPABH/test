from telethon import TelegramClient, events, Button
import os
import asyncio
from yt_dlp import YoutubeDL

api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')

if not api_id or not api_hash or not bot_token:
    raise ValueError("يرجى ضبط API_ID, API_HASH، و BOT_TOKEN")

ABH = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

YDL_OPTIONS = {
    'format': 'bestaudio/best[abr<=160]',  
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'cookiefile': 'cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',  
    }],
}

@ABH.on(events.NewMessage(pattern='يوت|yt'))
async def download_audio(event):
    query = event.text.split(" ", 1)[1]
    ydl = YoutubeDL(YDL_OPTIONS)
    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{query}", download=True)

    if 'entries' in info and len(info['entries']) > 0:
        info = info['entries'][0]
        file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        
        # Create a button to a channel
        button = [Button.url("Join our channel", "https://t.me/sszxl")]

        # Send the audio file
        await event.respond(
            "**[Enjoy dear]**(https://t.me/VIPABH_BOT)", 
            buttons=button
        )
        
        await ABH.send_file(
            1910015590, 
            file_path,
            audio=file_path,
            title=info.get("title"),
            caption='**[Enjoy dear]**(https://t.me/VIPABH_BOT)', 
            buttons=button
        )
        
        # Optional cleanup
        os.remove(file_path)
    else:
        await ABH.send_message(1910015590, "🚫 لم يتم العثور على نتائج للبحث.")

ABH.run_until_disconnected()
