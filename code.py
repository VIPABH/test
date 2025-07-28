from telethon.tl.types import MessageEntityUrl
from telethon import events, Button
from ABH import ABH  # type:ignore
from Resources import *
import asyncio
from telethon import events, types

# الرمز التعبيري الذي تريد استخدامه كرياكشن
REACTION = '❤️'  # يمكنك تغييره إلى: '🔥' أو '👍' أو غيرها

@ABH.on(events.NewMessage)
async def auto_reaction(event):
    try:
        await ABH.send_reaction(
            entity=event.chat_id,
            message_id=event.message.id,  # هذا هو التعديل المهم
            reaction=types.ReactionEmoji(emoticon=REACTION)
        )
    except Exception as e:
        print(f"فشل في إرسال الرياكشن: {e}")
