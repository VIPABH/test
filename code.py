import os
from telethon import TelegramClient, events, functions, types
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def send_larger_hint(event):

    CUSTOM_EMOJI_ID = 5276514176657812074

    try:

        # إرسال الرسالة
        msg = await ABH.send_message(
            event.chat_id,
            "نتيجتك للتخمين الحالي:",
            buttons=[
                [
                    types.KeyboardButtonCallback(
                        text="الرقم أكبر 📈",
                        data=b"check_score"
                    )
                ]
            ]
        )

        # إرسال التفاعل المخصص
        await ABH(functions.messages.SendReactionRequest(
            peer=event.chat_id,
            msg_id=msg.id,
            reaction=[
                types.ReactionCustomEmoji(
                    document_id=CUSTOM_EMOJI_ID
                )
            ],
            big=True
        ))

    except Exception as e:
        print(f"Error sending reaction: {e}")
