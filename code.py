import os
from telethon import TelegramClient, events, functions, types
from faster_whisper import WhisperModel
from ABH import *
from Resources import *

@ABH.on(events.NewMessage(incoming=True))
async def try_specific_reaction(event):
    # الـ ID المحدد الذي طلبته
    TARGET_EMOJI_ID = 5276048898555669761
    
    # نتخطى الأوامر لكي لا يتداخل الفحص
    if event.text.startswith('/'):
        return
        
    print(f"[⏳] محاولة التفاعل بالرمز: {TARGET_EMOJI_ID} على الرسالة رقم {event.id}...")
    
    try:
        await ABH(functions.messages.SendReactionRequest(
            peer=event.chat_id,
            msg_id=event.id,
            reaction=[
                types.ReactionCustomEmoji(
                    document_id=TARGET_EMOJI_ID
                )
            ]
        ))
        print("[✅] مذهل! السيرفر قبل التفاعل وتم إرساله بنجاح!")
        
    except Exception as e:
        print(f"[❌] رفض السيرفر التفاعل. السبب التقني المباشر:\n{e}")
