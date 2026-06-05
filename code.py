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
    await e.reply(f"![](tg://emoji?id=5372913502140766965) {await mention(e)}", parse_mode='md')
@ABH.on(events.NewMessage(pattern='^هاندلرز$'))
async def send_clean(e):
    handlers = ABH.list_event_handlers()
    
    if not handlers:
        return await e.reply("لا يوجد أي هاندلرز مسجلين!")
        
    # سنأخذ أول هاندلر كمثال ونطبع كل محتوياته لنعرف أين يختبئ الـ pattern
    first_callback, first_event = handlers[0]
    
    # جلب جميع الخصائص (Attributes) الموجودة داخل كائن الـ event
    event_attributes = list(first_event.__dict__.keys())
    
    debug_text = f"⚙️ **تقرير الفحص الداخلي للـ Event:**\n\n"
    debug_text += f"🔹 **اسم الدالة الأولى:** `{first_callback.__name__}`\n"
    debug_text += f"🔹 **نوع كائن الحدث:** `{type(first_event).__name__}`\n"
    debug_text += f"🔹 **الخصائص المتوفرة داخله:**\n`{event_attributes}`\n\n"
    
    # إذا كان هناك خاصية باسم filter، دعنا نرى ما بداخلها أيضاً
    if hasattr(first_event, 'filter') and first_event.filter:
        filter_attributes = list(first_event.filter.__dict__.keys())
        debug_text += f"🔍 **ماذا يوجد داخل الـ filter؟**\n`{filter_attributes}`\n"
        
    await e.reply(debug_text)
