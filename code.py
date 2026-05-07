from Resources import *
from ABH import *

@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def handle_whisper(event):
    # lock_key = f"lock:{event.chat_id}:همسة"
    # if r.get(lock_key) != b"True":
    #     await event.reply('اوامر الهمسة معطلة💔')
    #     return

    # تقطيع النص
    args = event.pattern_match.group(1).split()
    user_ids = []

    for item in args:
        try:
            # تحويل ذكي: إذا رقم يصير int، وإذا يوزر يبقى str
            target = int(item) if item.strip('-').isdigit() else item
            
            # جلب الكيان
            entity = await event.client.get_entity(target)
            
            # التأكد إن الحساب مو محذوف (Deleted Account)
            if hasattr(entity, 'deleted') and entity.deleted:
                continue # يتخطاه إذا محذوف
                
            user_ids.append(entity.id)
            
        except Exception:
            # إذا اليوزر غلط، الحساب محظور، أو أي مشكلة.. يتخطاه ببساطة
            continue

    if user_ids:
        await event.reply(f"تم استخراج الايديات بنجاح: {user_ids}")
    else:
        await event.reply("لم يتم العثور على مستخدمين صالحين (كل المعرفات خطأ أو حسابات محذوفة)!")
