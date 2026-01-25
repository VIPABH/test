from ABH import ABH
from telethon import events
import re

def parse_command(text):
    # النمط الذكي الذي صممناه
    pattern = r'(حظر عام|تقييد عام)\s+(@\w+|\d{5,10}|\d{2,3})(?:\s+(\d{5,10}|\d{2,3}))?'
    match = re.search(pattern, text)
    
    if not match:
        return None
        
    command = match.group(1)
    parts = [match.group(2), match.group(3)]
    
    user = user_id = duration = None
    
    for part in parts:
        if not part: continue
        if part.startswith('@'):
            user = part
        elif 5 <= len(part) <= 10:
            user_id = part
        elif 2 <= len(part) <= 3:
            if 10 <= int(part) <= 360:
                duration = part
                
    return command, user, user_id, duration

@ABH.on(events.NewMessage(pattern=r'^(حظر عام|تقييد عام)'))
async def handle_command(event):
    text = event.raw_text
    result = parse_command(text)
    
    if not result:
        # إذا لم يطابق النص النمط الأساسي إطلاقاً
        await event.reply("❌ تنسيق الأمر خاطئ.")
        return
        
    command, user, user_id, duration = result
    
    # بناء الرد لعرض النتائج حتى لو كانت None
    # استخدمنا f-string مع تحويل القيم لنصوص مباشرة
    response = (
        f"**📊 نتائج تحليل الأمر:**\n"
        f"**- نوع الأمر:** {command}\n"
        f"**- المستخدم:** {user}\n"
        f"**- الآيدي:** {user_id}\n"
        f"**- المدة:** {duration}"
    )

    await event.reply(response)
