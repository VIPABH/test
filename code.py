from Resources import *
from ABH import *

session = {}

@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def whisper_list_handler(e):
    # استخدام .split() لتحويل النص إلى قائمة كلمات بناءً على المسافات
    input_data = e.pattern_match.group(1).strip().split()
    
    # الآن input_data هي قائمة (List) بكل الكلمات بعد كلمة 'اهمس'
    await e.reply(str(input_data))
