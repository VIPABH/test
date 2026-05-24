import os
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    # نتخطى الأوامر
    if event.text.startswith('/'):
        return

    CUSTOM_EMOJI_ID = 5276514176657812074 
    
    # صياغة الـ HTML القياسية لتليجرام: نضع الإيموجي الحقيقي ⬆️ داخل التاج ليقوم المخصص بتغطيته
    text = f'الرقم الصحيح أكبر <tg-emoji emoji-id="{CUSTOM_EMOJI_ID}">⬆️</tg-emoji>'
    
    try:
        await ABH.send_message(
            event.chat_id,
            "هلا [❤️](tg://emoji?id=5206607081334906820)",
            parse_mode="md"
)
        await ABH.send_message(
            event.chat_id, 
            text, 
            # parse_mode='html' # تفعيل الـ HTML بدلاً من الماركداون
        )
        print("[✅] تم إرسال الرسالة بالإيموجي المخصص بنجاح!")
    except Exception as e:
        print(f"[❌] حدث خطأ أثناء الإرسال: {e}")
