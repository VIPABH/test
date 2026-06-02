from telethon import types, events
from ABH import *
from Resources import *


@ABH.on(events.NewMessage(pattern='/test'))
async def send_clean(e):
    # 1. نضع السهم العادي كنص للرسالة
    text = "⬆️"
    
    # 2. ننشئ كائن الإيموجي المميز مباشرة ونحدد أن طوله 2 (لأن السهم ياخذ مساحتين بالـ UTF-16)
    emoji_entity = types.MessageEntityCustomEmoji(
        offset=0, 
        length=2, 
        document_id=5372913502140766965
    )
    
    # 3. نرسل الرسالة مباشرة
    await e.reply(text, formatting_entities=[emoji_entity])
    await e.reply(f"![⬆️](tg://emoji?id=5372913502140766965) {await mention(e)}", parse_mode='md2')
