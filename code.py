from telethon import types, events
from ABH import *
from Resources import *

import re
import time
from telethon import events

# --- 1. إعداد المتغيرات العامة وقواعد البيانات ---
# ABH = ... (اسم البوت الخاص بك)
# r = ... (متغير الـ Redis الخاص بك)

all_filters_list = []
CACHE_ENGINE = {}
CACHE_TTL = 120 

# --- 2. دالة أوزان الرتب والمقارنة ---
def authers(required_rank, user_rank) -> bool:
    """
    تقوم بالمقارنة بين الرتبة المطلوبة للأمر ورتبة المستخدم الحالية.
    """
    hierarchy = {
        "المالك": 4,
        "المطور الثانوي": 3,
        "المساعد": 2,
        "المعاون": 1,
        "العضو": 0
    }
    
    user_weight = hierarchy.get(user_rank, 0)
    required_weight = hierarchy.get(required_rank, 1) # الافتراضي معاون إذا لم يحدد
    
    return user_weight >= required_weight


# --- 3. دالة تنظيف وفصل الأنماط المتقدمة (Regex) ---
def clean_and_split_pattern(pattern_str):
    if not pattern_str:
        return []
        
    clean = pattern_str.strip("^$()")
    clean = re.sub(r'\[هة\]', 'ة', clean)
    clean = re.sub(r'\[ه\|ة\]', 'ة', clean)
    clean = re.sub(r'\(\.\+\)', '...', clean)
    
    match_group = re.search(r'\((.+?)\)', pattern_str)
    if match_group:
        prefix = pattern_str.split('(')[0].strip("^$ ")
        suffix = pattern_str.split(')')[-1].strip("^$ ")
        options = match_group.group(1).split('|')
        results = []
        for opt in options:
            opt_clean = re.sub(r'\[هة\]', 'ة', opt)
            full_command = f"{prefix} {opt_clean}".strip()
            if suffix:
                full_command = f"{full_command} {suffix}".strip()
            results.append(f"/{full_command}" if pattern_str.startswith('/') else full_command)
        return results
    elif '|' in clean:
        return [re.sub(r'\[هة\]', 'ة', opt).strip() for opt in clean.split('|')]
    else:
        return [clean]


# --- 4. دالة تحميل الفلاتر الحالية للبوت ---
def load_all_filters():
    global all_filters_list
    handlers = ABH.list_event_handlers()
    all_filters_list.clear()
    
    for callback, event in handlers:
        raw_pattern = None
        if hasattr(event, 'pattern') and event.pattern:
            if hasattr(event.pattern, '__self__') and hasattr(event.pattern.__self__, 'pattern'):
                raw_pattern = event.pattern.__self__.pattern
            elif hasattr(event.pattern, 'pattern'):
                raw_pattern = event.pattern.pattern
            else:
                raw_pattern = str(event.pattern)
                
        if raw_pattern:
            all_filters_list.extend(clean_and_split_pattern(raw_pattern))
            
    all_filters_list = list(set(all_filters_list))


# --- 5. محرك الأوامر والاختصارات وجدار الحماية المركزي ---
@ABH.on(events.NewMessage(incoming=True))
async def execute_alias_engine(event):
    if hasattr(event, 'alias_processed') and event.alias_processed:
        return
    if not event.raw_text:
        return
        
    global CACHE_ENGINE
    chat_id = event.chat_id
    current_time = time.time()
    
    # تحديث كاش الاختصارات من الـ Redis عند انتهاء الـ TTL
    if chat_id not in CACHE_ENGINE or (current_time - CACHE_ENGINE[chat_id]['last_update']) > CACHE_TTL:
        all_aliases = r.hgetall(f"cmd:{chat_id}")
        
        if not all_aliases:
            CACHE_ENGINE[chat_id] = {'aliases': {}, 'sorted_keys': [], 'last_update': current_time}
            return
            
        processed_data = {}
        for k, v in all_aliases.items():
            # بدون استخدام decode يدوياً بناءً على طلبك
            key = str(k).strip()
            val = str(v).strip()
            processed_data[key] = val
            
        sorted_keys = sorted(processed_data.keys(), key=len, reverse=True)
        CACHE_ENGINE[chat_id] = {
            'aliases': processed_data,
            'sorted_keys': sorted_keys,
            'last_update': current_time
        }
        
    cache = CACHE_ENGINE[chat_id]
    if not cache['aliases']:
        return
        
    text = event.raw_text.strip()
    
    # البحث عن أي اختصار يطابق نص الرسالة الحالية
    for shortcut in cache['sorted_keys']:
        pattern = rf"^{re.escape(shortcut)}(\s+|$)"
        match = re.match(pattern, text)
        
        if match:
            real_cmd = cache['aliases'][shortcut]  # الأمر الحقيقي المترجم
            args = text[len(shortcut):].strip()
            new_text = f"{real_cmd} {args}".strip()
            
            # --- 🛡️ جدار الحماية المركب (تأكيد الصلاحيات والقيود) 🛡️ ---
            cmd_name_clean = real_cmd[1:].strip() if real_cmd.startswith('/') else real_cmd.strip()
            
            # جلب تقييد هذا الأمر الصافي من الـ Redis (تم إلغاء الـ decode هنا أيضاً)
            restricted_to = r.hget(f"group:{chat_id}:restricted_commands", cmd_name_clean)
            
            if restricted_to:
                restricted_to = str(restricted_to).strip()
                
                # جلب رتبة المستخدم الحالية من دالتك الأساسية
                user_rank = await auth(event)
                user_rank = str(user_rank).strip()
                
                # التحقق من الأوزان؛ إذا لم تكن صلاحيته كافية نقفل التنفيذ فوراً
                if not authers(restricted_to, user_rank):
                    await event.reply(f"⚠️ عذراً، أمر (**{cmd_name_clean}**) مقيد لرتب أعلى في هذه المجموعة.")
                    raise events.StopPropagation  # كسر السلسلة ومنع وصول الحدث للهاندلرز 🛑
            # --- 🛡️ نهاية جدار الحماية المركزي 🛡️ ---
            
            # تعديل نص الرسالة للحدث الحالي بعد تخطي الحماية بنجاح
            event.alias_processed = True  
            event.message.message = new_text
            
            # إعادة توجيه الحدث المحدث يدوياً على الهاندلرز المطابقة
            for handler, event_builder in ABH.list_event_handlers():
                if handler == execute_alias_engine:
                    continue
                if isinstance(event_builder, events.NewMessage):
                    if event_builder.filter(event):
                        await handler(event)                        
                        
            raise events.StopPropagation


# --- 6. أمر التحكم بالتقييد (للمالك فقط لتعديل القيود بالمجموعة) ---
@ABH.on(events.NewMessage(pattern=r"^/تقييد (.*) لـ (المالك|المطور الثانوي|المساعد|المعاون)"))
async def restrict_command_config(event):
    chat_id = event.chat_id
    
    # التحقق من أن منفذ أمر التقييد نفسه هو "المالك" عبر دالتك
    user_rank = await auth(event)
    if str(user_rank).strip() != "المالك":
        await event.reply("❌ هذا الأمر خاص بمالك المجموعة فقط.")
        return
        
    command_to_restrict = event.pattern_match.group(1).strip()
    target_rank = event.pattern_match.group(2).strip()
    
    # حفظ التقييد في الـ Redis الخاص بالمجموعة الحالية ليعمل مع جدار الحماية أعلاه
    r.hset(f"group:{chat_id}:restricted_commands", command_to_restrict, target_rank)
    
    await event.reply(f"🔒 تم تقييد أمر (**{command_to_restrict}**) بنجاح، أصبح متاحاً لرتبة **{target_rank}** فما فوق داخل هذه المجموعة.")


# --- 7. أمر تجربة (للمحاكاة والفحص) ---
@ABH.on(events.NewMessage(pattern=r"^/طرد(.*)"))
async def test_ban_command(event):
    """
    أمر تجريبي لفحص جدار الحماية وعملية التوجيه المباشر.
    """
    # إذا وصل البوت إلى هنا، فهذا يعني أن المستخدم تخطى جدار الحماية بنجاح!
    await event.reply("✅ تم تفعيل أمر التجربة بنجاح! صلاحيتك تسمح باستخدام هذا الأمر.")
