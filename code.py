import os
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    CUSTOM_EMOJI_ID = 5276514176657812074 
    
    # نستخدم صيغة التنسيق المدمجة لتليجرام (الإيموجي المخصص يعامل كرابط بروتوكول tg://)
    # النص المكتوب بين الـ [] هو الذي سيظهر فوقه الإيموجي، وضعنا مسافة سحرية مخفية
    text = f"الرقم الصحيح أكبر [  ](tg://emoji?id={CUSTOM_EMOJI_ID})"
    
    await ABH.send_message(
        event.chat_id, 
        text, 
        parse_mode='md' # تفعيل الماركداون لمعالجة الرابط كإيموجي مخصص
    )
