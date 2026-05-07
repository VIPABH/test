from Resources import *
from ABH import *

@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def handle_whisper(event):
    # استخراج اليوزرات من النص وتحويلهم إلى لستة
    args = event.pattern_match.group(1).split()
    
    try:
        # تليثون تدعم تمرير لستة كاملة لـ get_entity
        entities = await event.client.get_entity(args)
        
        # استخراج الـ ID من كل entity تم جلبها
        # ملاحظة: إذا كان عنصر واحد ترجع object، إذا أكثر ترجع list
        if isinstance(entities, list):
            user_ids = [e.id for e in entities]
        else:
            user_ids = [entities.id]

        if user_ids:
            await event.reply(f"الايديات المستخرجة: {user_ids}")
            
    except Exception as e:
        await event.reply(f"صار خطأ أو المعرفات غلط: {str(e)}")
