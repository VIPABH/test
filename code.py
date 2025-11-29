from telethon import events
from Resources import *
from ABH import ABH
messages_cache = {}
@ABH.on(events.MessageEdited)
async def edited_msg(event):
    msg_id = event.message.id

    old_text = messages_cache.get(msg_id, None)      # النص قبل التعديل
    new_text = event.message.message                 # النص بعد التعديل

    # حدث التحديث في التخزين
    messages_cache[msg_id] = new_text

    await event.reply(
        f"النص قبل التعديل:\n{old_text}\n\n"
        f"النص بعد التعديل:\n{new_text}"
    )
