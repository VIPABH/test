from Resources import *
from ABH import *

@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def handle_whisper(event):
    # lock_key = f"lock:{event.chat_id}:همسة"
    # if r.get(lock_key) != b"True":
    #     await event.reply('اوامر الهمسة معطلة💔')
    #     return

    # استخراج الكلمات
    args = event.pattern_match.group(1).split()
    
    # تحويل البيانات: إذا رقم يصير int، وإذا يوزر يبقى str
    # الـ strip('-') حتى يدعم الايديات السالبة (مثل ايديات القنوات والمجموعات)
    processed_ids = [int(i) if i.strip('-').isdigit() else i for i in args]
    
    try:
        # تمرير القائمة "المختلطة" (int و str) لـ get_entity
        entities = await event.client.get_entity(processed_ids)
        
        # استخراج الايديات في لستة واحدة
        if isinstance(entities, list):
            user_ids = [e.id for e in entities]
        else:
            user_ids = [entities.id]

        if user_ids:
            # هنا صار عندك لستة user_ids جاهزة تحتوي على أرقام فقط
            await event.reply(f"تم استخراج الايديات بنجاح: {user_ids}")
            
    except Exception as e:
        await event.reply(f"خطأ في جلب البيانات: {str(e)}")
