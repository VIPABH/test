from telethon.tl.types import MessageEntityUrl
from telethon import events, Button
from ABH import ABH  # type:ignore
from Resources import *
import asyncio
from telethon import events, types
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import InputPeerUser, ReactionEmoji

@ABH.on(events.NewMessage)
async def react_to_message(chat_id, message_id, emoji='❤️'):
    await client(SendReactionRequest(
        peer=chat_id,
        msg_id=message_id,
        reaction=[ReactionEmoji(emoticon=emoji)],
        big=False  # ضع True إذا أردت التفاعل الكبير (Big Reaction)
    ))
