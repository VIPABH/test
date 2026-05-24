import os
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    text = "الرقم الصحيح أكبر "
    placeholder = " ⬆️" # مساحة نصية ليركب فوقها الإيموجي المخصص
    
    # الـ ID الذي أرسلته أنت
    CUSTOM_EMOJI_ID = 5276514176657812074 
    
    entity = types.MessageEntityCustomEmoji(
        offset=len(text.encode('utf-16-le')) // 2,
        length=len(placeholder.encode('utf-16-le')) // 2,
        document_id=CUSTOM_EMOJI_ID
    )
    
    await ABH.send_message(
        eventزchat_id, 
        text + placeholder, 
        formatting_entities=[entity]
    )
