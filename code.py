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
import re

def clean_and_split_pattern(pattern_str):
    """
    تنظيف الـ Pattern وتحويله إلى قائمة من الكلمات النظيفة
    """
    if not pattern_str:
        return []
        
    # 1. تنظيف الرموز الأساسية للريجكس من البداية والنهاية
    clean = pattern_str.strip("^$()")
    
    # 2. معالجة الحروف البديلة مثل [هة] أو [ه|ة] وتحويلها لشكل بسيط (مثلاً ه)
    clean = re.sub(r'\[هة\]', 'ة', clean)
    clean = re.sub(r'\[ه\|ة\]', 'ة', clean)
    clean = re.sub(r'\(\.\+\)', '...', clean)  # تحويل الجلب المفتوح (.+) إلى نقاط
    
    # 3. إذا كان الـ Pattern يحتوي على خيارات مجمعة بـ | داخل أقواس
    # مثال: ^اوامر (الرفع|الادارة)$
    match_group = re.search(r'\((.+?)\)', pattern_str)
    
    if match_group:
        # استخراج الكلمات المشتركة خارج الأقواس
        prefix = pattern_str.split('(')[0].strip("^$ ")
        suffix = pattern_str.split(')')[-1].strip("^$ ")
        
        # تفكيك الخيارات الداخلية بناءً على علامة |
        options = match_group.group(1).split('|')
        
        # دمج الكلمات المشتركة مع كل خيار
        results = []
        for opt in options:
            # تنظيف الخيار نفسه من الحروف البديلة
            opt_clean = re.sub(r'\[هة\]', 'ة', opt)
            
            # بناء الأمر الكامل
            full_command = f"{prefix} {opt_clean}".strip()
            if suffix:
                full_command = f"{full_command} {suffix}".strip()
            results.append(f"/{full_command}" if pattern_str.startswith('/') else full_command)
            
        return results
        
    # 4. إذا كان يحتوي على علامة | بدون أقواس
    elif '|' in clean:
        return [re.sub(r'\[هة\]', 'ة', opt).strip() for opt in clean.split('|')]
        
    # 5. إذا كان أمراً عادياً صافياً
    else:
        return [clean]

# ----------------- أمر الهاندلرز المطور -----------------

@ABH.on(events.NewMessage(pattern='^هاندلرز$'))
async def send_clean(e):
    handlers = ABH.list_event_handlers()
    text_response = "📋 **قائمة الأوامر المنقحة والمنظفة:**\n\n"
    
    for callback, event in handlers:
        raw_pattern = None
        
        # استخراج الـ Pattern الخام كما فعلنا سابقاً
        if hasattr(event, 'pattern') and event.pattern:
            if hasattr(event.pattern, '__self__') and hasattr(event.pattern.__self__, 'pattern'):
                raw_pattern = event.pattern.__self__.pattern
            elif hasattr(event.pattern, 'pattern'):
                raw_pattern = event.pattern.pattern
            else:
                raw_pattern = str(event.pattern)
                
        elif hasattr(event, 'func') and event.func:
            raw_pattern = f"دالة فحص: {event.func.__name__}"
            
        # إذا وجدنا الـ Pattern الخام، نقوم بتنقيحه وتحويله لـ List
        if raw_pattern:
            cleaned_list = clean_and_split_pattern(raw_pattern)
            
            # تحويل القائمة إلى نص منسق للعرض
            if len(cleaned_list) > 1:
                # إذا كان يحتوي على خيارات متعددة، نعرضها كقائمة فرعية
                formatted_pattern = ", ".join([f"`{cmd}`" for cmd in cleaned_list])
            elif cleaned_list:
                formatted_pattern = f"`{cleaned_list[0]}`"
            else:
                formatted_pattern = f"`{raw_pattern}`"
                
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔻 **الأوامر المفككة:** {formatted_pattern}\n\n"
        else:
            text_response += f"🔹 **الدالة:** `{callback.__name__}`\n🔺 _لا يوجد لها pattern محدد_\n\n"
            
    await e.reply(text_response)
