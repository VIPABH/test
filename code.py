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
    text_response = "📋 **قائمة الهاندلرز والفلتر الخاص بها:**\n\n"
    
    for callback, event in handlers:
        pattern_text = None
        
        if hasattr(event, 'pattern') and event.pattern:
            # 1. إذا كان الـ pattern عبارة عن دالة (method) مثل match
            if hasattr(event.pattern, '__self__') and hasattr(event.pattern.__self__, 'pattern'):
                pattern_text = event.pattern.__self__.pattern
            # 2. إذا كان كائن ريجكس مباشر
            elif hasattr(event.pattern, 'pattern'):
                pattern_text = event.pattern.pattern
            # 3. إذا كان نصاً عادياً
            else:
                pattern_text = str(event.pattern)
                
        elif hasattr(event, 'func') and event.func:
            pattern_text = f"دالة فحص مخصصة: {event.func.__name__}"
            
        # بناء الرسالة
        if pattern_text:
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔻 **الـ Pattern:** `{pattern_text}`\n\n"
        else:
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔺 _لا يوجد لها pattern محدد_\n\n"
            
    await e.reply(text_response)
