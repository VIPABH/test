from telethon.tl.types import MessageEntityUrl
from telethon import events, Button
from ABH import ABH  # type:ignore
from Resources import *
import asyncio

REACTION = '❤️'  # يمكنك تغيير الرياكشن إلى أي رمز تعبيري

@ABH.on(events.NewMessage)
async def auto_react(event):
    try:
        await ABH.send_reaction(
            entity=event.chat_id,
            message_id=event.message.id,
            reaction=types.ReactionEmoji(emoticon=REACTION)
        )
    except Exception as e:
        print(f"خطأ أثناء إرسال الرياكشن: {e}")
