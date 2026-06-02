from telethon import types, events
from ABH import *

@ABH.on(events.NewMessage(pattern='/test'))
async def send_clean(e):
    # افترضت أن لديك كائن الـ target مسبقاً في كودك
    user_name = target.first_name  # سيظهر كاسم عادي بدون رابط (حتى لو كان فيه رموز $%_)
    emoji_id = 5372913502140766965

    # 1. نكتب الاسم كنص مجرد (عادي)، ونضع الماركداون فقط للرمز/الإيموجي
    raw_text = f"المستخدم ( {user_name} ) ما عنده قيود [⬆️](tg://emoji?id={emoji_id})"
    
    # 2. تفكيك النص وحساب أبعاد الرمز بدقة UTF-16 لتفادي خطأ الـ Bounds
    text, entities = await e._client._parse_message_text(raw_text, parse_mode='md')
    
    # 3. إرسال النص الصافي مع كائن الرمز المخصص
    await e.reply(text, formatting_entities=entities)
