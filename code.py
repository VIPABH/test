from Resources import *
from ABH import *
session = {}
@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def whisper_list_handler(event):
    input_data = event.pattern_match.group(1).strip()    
    raw_list = input_data.split()
    target_list = []  
    message_content = []
    for item in raw_list:
        if item.startswith('@') or item.isdigit():
            target_list.append(item)
        else:
            message_content = raw_list[raw_list.index(item):]
            break            
    if not target_list or not message_content:
        return await event.reply("الاستخدام: اهمس @يوزر1 @يوزر2 نص الرسالة")
    final_message = " ".join(message_content)    
    await event.reply(f"تم تجهيز الهمسة لـ {len(target_list)} مستخدم.\nالقائمة: {target_list}")
