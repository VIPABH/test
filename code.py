import os
from telethon import TelegramClient, events, types # أضفنا types هنا للتأكيد
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    text = "الرقم الصحيح أكبر"
    # نستخدم مسافة عادية كقاعدة للإيموجي لمنع تضارب الـ UTF-16
    placeholder = " " 
    
    CUSTOM_EMOJI_ID = 5276514176657812074 
    
    # حساب الموقع بدقة بالاعتماد على الترميز الصافي
    text_utf16_len = len(text.encode('utf-16-le')) // 2
    placeholder_utf16_len = len(placeholder.encode('utf-16-le')) // 2
    
    entity = types.MessageEntityCustomEmoji(
        offset=text_utf16_len,
        length=placeholder_utf16_len,
        document_id=CUSTOM_EMOJI_ID
    )
    
    await ABH.send_message(
        event.chat_id, 
        text + placeholder, 
        formatting_entities=[entity]
    )
