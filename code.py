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
        
        # 1. فحص إذا كان الـ _regex موجود مباشرة في الحدث (في بعض النسخ المعدلة)
        if hasattr(event, '_regex') and event._regex:
            pattern_text = event._regex.pattern
            
        # 2. الطرق القياسية لـ Telethon للوصول للفلتر بشتى صوره
        elif hasattr(event, 'filter') and event.filter:
            # إذا كان الفلتر يحتوي على الـ _regex مباشرة
            if hasattr(event.filter, '_regex') and event.filter._regex:
                pattern_text = event.filter._regex.pattern
            # إذا كان الفلتر عبارة عن كائن يحتوي على خاصية pattern نصية
            elif hasattr(event.filter, 'pattern') and event.filter.pattern:
                pattern_text = event.filter.pattern
                
        # إذا وجدنا الفلتر نقوم بإضافته للنص، وإلا نكتب لا يوجد
        if pattern_text:
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔻 **الـ Pattern:** `{pattern_text}`\n\n"
        else:
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔺 _لا يوجد لها pattern محدد_\n\n"
            
    # إرسال النتيجة في رسالة واحدة مرتبة بدلاً من إرسال رسائل متعددة تسبب سبام للبوت
    await e.reply(text_response)
