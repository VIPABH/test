from ABH import ABH
from telethon import events
import re

def parse_command(text):
    pattern = r'(حظر عام|تقييد عام)\s+(@\w+|\d{5,10}|\d{2,3})(?:\s+(\d{5,10}|\d{2,3}))?'
    match = re.search(pattern, text)
    
    if not match:
        return None  # نرجع None لسهولة الفحص لاحقاً
        
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

    response = [f"**نوع الأمر:** {result[0] if result else ' بالرد'}"]
    if not result:
        await event.reply(str(response))
        return 
    command, user, user_id, duration = result    
    if user: response.append(f"**المستخدم:** {user}")
    if user_id: response.append(f"**الآيدي:** `{user_id}`")
    if duration: response.append(f"**المدة:** {duration} دقيقة")    
    if not user and not user_id:
        await event.reply("⚠️ يرجى تحديد مستخدم أو آيدي صحيح.")
        return
    await event.reply("\n".join(response))
