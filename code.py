from telethon import types, events
from ABH import *

@ABH.on(events.NewMessage(pattern='/test'))
async def send_clean(e):
    emoji_id = 5372913502140766965

    # 1. النص يحتوي فقط على الرمز التعبيري وبجانبه رابط الآيدي الخاص به
    raw_text = f"[⬆️](tg://emoji?id={emoji_id})"
    
    # 2. حساب الأبعاد تلقائياً للرمز بمفرده
    text, entities = await e._client._parse_message_text(raw_text, parse_mode='md')
    
    # 3. إرسال الإيموجي المميز فقط
    await e.reply(text, formatting_entities=entities)
