import os
import tempfile
import speech_recognition as sr
from telethon import events
from pydub import AudioSegment
import pyttsx3
from ABH import ABH as client # استيراد الكلاينت من ملف ABH.py

# ===== إعداد الصوت =====
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
import random
import asyncio

# بيانات حساب User

EMOJIS = ['👍', '🕊', '❤️']

@client.on(events.NewMessage)
async def auto_react(event):
    try:
        # اختيار إيموجي عشوائي
        emoji = random.choice(EMOJIS)

        # إرسال رد فعل على الرسالة الجديدة
        await client(SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.message.id,
            reaction=[ReactionEmoji(emoticon=emoji)],
            big=True
        ))
        print(f"✅ تم وضع رد فعل {emoji} على رسالة {event.message.id}")

    except Exception as e:
        print(f"❌ خطأ أثناء وضع رد فعل: {e}")
