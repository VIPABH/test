import os
import aiohttp
from mutagen.mp3 import MP3
from telethon.tl.types import DocumentAttributeAudio
from telethon import events, TelegramClient
api_id = os.getenv('API_ID')      
api_hash = os.getenv('API_HASH')  
bot_token = os.getenv('BOT_TOKEN')
ABH = TelegramClient('code', api_id, api_hash).start(bot_token=bot_token)
@ABH.on(events.NewMessage)
async def replys(event):
    text = event.text
    x = "ابن هاشم"
    if x in text:
        await event.reply("تفضل حبيبي")
    else:
        return
ABH.run_until_disconnected()
