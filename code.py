from ABH import ABH as client
from telethon import  events

from telethon import TelegramClient, events
from telethon.tl.types import ReactionEmoji

from telethon import events
from telethon.tl.types import UpdateMessageReactions, UpdateBotMessageReactions

@client.on(events.Raw)
async def catch_reaction_live(event):
    # هذا الحدث يعمل بشكل فوري ولحظي عندما يضغط أي شخص على زر تفاعل
    if isinstance(event, (UpdateMessageReactions, UpdateBotMessageReactions)):
        msg_id = event.msg_id
        peer = event.peer
        reactions_list = event.reactions.results
        
        print(f"🔥 تم رصد تفاعل جديد على الرسالة ID: {msg_id}")
        
        for r in reactions_list:
            emoji = getattr(r.reaction, 'emoticon', 'Custom')
            count = r.count
            print(f"الإيموجي: {emoji} | العدد الحالي: {count}")
            
            # (اختياري) يمكنك هنا حفظ الـ msg_id والتفاعل في قاعدة بياناتك 
            # ليقوم البوت بعرضه لاحقاً عندما يطلبه المستخدم.
