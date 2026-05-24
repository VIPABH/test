import os
from telethon import TelegramClient, events
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, types.MessageEntityCustomEmoji):
                print(f"Custom Emoji ID: {entity.document_id}")
