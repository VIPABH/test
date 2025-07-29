from telethon.tl.types import MessageEntityUrl
from telethon import events, Button
from ABH import ABH  # type:ignore
from Resources import *
import asyncio
from telethon import events, types
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import InputPeerUser, ReactionEmoji
print(telethon.__version__)
@ABH.on(events.NewMessage(pattern='ها'))
async def react_to_message(event):
    await ABH(SendReactionRequest(
        peer=event.chat_id,
        msg_id=event.id,
        reaction=[ReactionEmoji(emoticon='❤️')],
        big=True
    ))
