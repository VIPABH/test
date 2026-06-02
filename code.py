from telethon import types, events
from ABH import *
@ABH.on(events.NewMessage(pattern='/test'))
async def send_clean(e):
    user_name = target.first_name  # الاسم حتى لو كان مليء بالرموز $%_
    user_id = target.id
    emoji_id = 5372913502140766965

    # 1. نكتب النص باستخدام الماركداون لتسهيل الدمج فقط
    raw_text = f"المستخدم ( [{user_name}](tg://user?id={user_id}) ) ما عنده قيود [⬆️](tg://emoji?id={emoji_id})"
    
    # 2. نطلب من Telethon تفكيك النص وحساب الأبعاد بدقة تليجرام الرسمية (UTF-16)
    # الدالة تُرجع: النص مجرد تماماً + الـ Entities محسوبة المربعات الـ Bounds مية بالمية
    text, entities = await e._client._parse_message_text(raw_text, parse_mode='md')
    
    # 3. نرسل النص الصافي والـ Entities الجاهزة بأمان
    await e.reply(text, formatting_entities=entities)
