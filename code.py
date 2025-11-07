from telethon import events

last_event_id = None  # متغير عالمي لتخزين آخر حدث تم التعامل معه

@ABH.on(events.ChatAction)
async def on_chat_action(event):
    global last_event_id
    me = await ABH.get_me()
    
    # تحقق من التكرار
    if event.id == last_event_id:
        return  # تجاهل الحدث إذا سبق التعامل معه
    last_event_id = event.id

    # تحقق من إضافة الحساب نفسه فقط
    if event.user_added and event.user_id == me.id:
        await event.reply('تمت إضافة الحساب نفسه')
