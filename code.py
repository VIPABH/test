import os, random
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    # تم إضافة علامات الاقتباس \" حول الـ ID لتفادي مشاكل الـ HTML
    custom_emoji = lambda emoji: f'<tg-emoji emoji-id="{random.choice(emoji)}">⬆️</tg-emoji>'
    
    # تم إضافة parse_mode='html' في نهاية سطر الإرسال
    await event.reply(
        f"{custom_emoji([5364105043907716258, 5422354988103901774, 5974388500458375909, 5469718869536940860, 5422354988103901774, 5348420849839912384, 5435891415055878798])}", 
        parse_mode='html'
    )
