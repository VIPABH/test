import yt_dlp, os, re, time, json, requests
from youtube_search import YoutubeSearch as Y88F8
from ABH import *
from Resources import *

ttl_seconds = 10  # مدة التدمير الذاتي بالثواني (غيرها مثل ما تريد)

@ABH.on(events.NewMessage)
async def s(e):
    await ABH.send_file(
        e.chat_id,
        file='موارد/photo_2025-02-10_11-40-17.jpg',
        video_note=False,
        supports_streaming=True,
        ttl_seconds=ttl_seconds
    )
