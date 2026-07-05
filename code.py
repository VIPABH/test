from ABH import *
import asyncio, yt_dlp, json, os, time, urllib.request
from telethon.tl.types import DocumentAttributeAudio, InputDocument
from concurrent.futures import ThreadPoolExecutor
from Resources import *
from telethon import events
from telethon.tl.types import MessageEntityMentionName
@ABH.on(events.NewMessage(pattern=r".?ترحيب"))
async def send_welcome(event):
    user_id = 8829795448  # أيدي الشخص
    name = "بايو Noor."
    text = f"نورت قروبنا يـ {name} 🥂✨"
    start = text.find(name)
    end = start + len(name)
    entity = MessageEntityMentionName(offset=start, length=len(name), user_id=user_id)
    await event.reply(text, formatting_entities=[entity])
