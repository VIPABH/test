import os
from telethon import TelegramClient, events, functions, types
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):
    CUSTOM_EMOJI_ID = 5276514176657812074 
    
    try:
        # إرسال التفاعل (Reaction) على الرسالة الحالية التي وصلت للبوت
        await ABH(functions.messages.SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.id,
            reaction=[
                types.ReactionCustomEmoji(
                    document_id=CUSTOM_EMOJI_ID
                )
            ]
        ))
    except Exception as e:
        print(f"Error sending reaction: {e}")
