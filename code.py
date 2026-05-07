from Resources import *
from ABH import *
@ABH.on(events.NewMessage(pattern=r'^اهمس (.*)'))
async def handle_whisper(event):
    # lock_key = f"lock:{event.chat_id}:همسة"
    # if r.get(lock_key) != b"True":
    #     await event.reply('اوامر الهمسة معطلة💔')
    #     return
    args = event.pattern_match.group(1).split()    
    processed_ids = [int(i) if i.strip('-').isdigit() else i for i in args]    
    try:
        entities = await event.client.get_entity(processed_ids)        
        if isinstance(entities, list):
            user_ids = [e.id for e in entities]
        else:
            user_ids = [entities.id]
        if user_ids:
            await event.reply(f"تم استخراج الايديات بنجاح: {user_ids}")
    except Exception as e:
        pass
